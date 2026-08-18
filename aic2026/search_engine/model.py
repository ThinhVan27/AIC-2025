from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image
from transformers import AutoModel, AutoProcessor, XLMRobertaTokenizer

try:
    from .config import SearchConfig, DEFAULT_CONFIG
    from .utils import l2_normalize, load_image, normalize_model_name
except ImportError:  # Allow `python model.py` from this directory.
    from config import SearchConfig, DEFAULT_CONFIG
    from utils import l2_normalize, load_image, normalize_model_name


class BaseEncoder:
    vector_size: int

    def encode_text(self, text: str) -> np.ndarray:
        raise NotImplementedError

    def encode_image(self, image: str | Path | Image.Image) -> np.ndarray:
        raise NotImplementedError


class BEIT3Encoder(BaseEncoder):
    vector_size = 1024

    def __init__(self, config: SearchConfig):
        self.config = config
        self.device = torch.device(config.device if torch.cuda.is_available() or config.device == "cpu" else "cpu")
        beit3_dir = config.base_dir / "beit3"
        previous_utils = sys.modules.pop("utils", None)
        sys.path.insert(0, str(beit3_dir))
        try:
            from modeling_finetune import beit3_large_patch16_384_retrieval
        finally:
            if sys.path[0] == str(beit3_dir):
                sys.path.pop(0)
            if previous_utils is not None:
                sys.modules["utils"] = previous_utils

        self.model = beit3_large_patch16_384_retrieval(pretrained=True)
        checkpoint = torch.load(config.beit3_checkpoint, map_location="cpu")
        state_dict = checkpoint.get("model", checkpoint)
        self.model.load_state_dict(state_dict, strict=False)
        self.model.to(self.device).eval()
        self.tokenizer = XLMRobertaTokenizer(str(config.beit3_spm))
        self.image_transform = T.Compose(
            [
                T.Resize((384, 384), interpolation=T.InterpolationMode.BICUBIC),
                T.ToTensor(),
                T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ]
        )

    def encode_text(self, text: str) -> np.ndarray:
        tokens = self.tokenizer(
            [text],
            padding=True,
            truncation=True,
            max_length=100,
            return_tensors="pt",
        )
        with torch.inference_mode():
            _, text_embedding = self.model(
                image=None,
                text_description=tokens["input_ids"].to(self.device),
                padding_mask=(1 - tokens["attention_mask"]).bool().to(self.device),
                only_infer=True,
            )
        return l2_normalize(text_embedding[0].detach().cpu().numpy().astype(np.float32))

    def encode_image(self, image: str | Path | Image.Image) -> np.ndarray:
        img = load_image(image)
        tensor = self.image_transform(img).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            image_embedding, _ = self.model(image=tensor, text_description=None, padding_mask=None, only_infer=True)
        return l2_normalize(image_embedding[0].detach().cpu().numpy().astype(np.float32))


class JinaOmniEncoder(BaseEncoder):
    vector_size = 1024

    def __init__(self, model_name: str, config: SearchConfig):
        self.model_name = model_name
        self.device = torch.device(config.device if torch.cuda.is_available() or config.device == "cpu" else "cpu")
        self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
            default_task="retrieval",
            modality="vision",
            dtype=torch.float32
        )
        self.model.to(self.device).eval()

    def encode_text(self, text: str) -> np.ndarray:
        with torch.inference_mode():
            inputs = self.processor(text=f"Query: {text}", return_tensors="pt").to(self.device)
            output = self.model.embed(**inputs).to(torch.float32)
            print(output)
        return l2_normalize(output[0].detach().cpu().numpy())

    def encode_image(self, image: str | Path | Image.Image) -> np.ndarray:
        img = load_image(image)
        with torch.inference_mode():
            inputs = self.processor(
                images=img,
                text="Query: <|vision_start|><|image_pad|><|vision_end|>",
                return_tensors="pt",
            ).to(self.device)
            output = self.model.embed(**inputs).to(torch.float32)
        return l2_normalize(output[0].detach().cpu().numpy())


class OpenCLIPEncoder(BaseEncoder):
    def __init__(self, model_name: str, vector_size: int, config: SearchConfig):
        import open_clip

        self.model_name = model_name
        self.vector_size = vector_size
        self.device = torch.device(config.device if torch.cuda.is_available() or config.device == "cpu" else "cpu")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(model_name)
        self.tokenizer = open_clip.get_tokenizer(model_name)
        self.model.to(self.device).eval()

    def encode_text(self, text: str) -> np.ndarray:
        context_length = getattr(self.model, "context_length", 77)
        tokens = self.tokenizer([text], context_length=context_length).to(self.device)
        with torch.inference_mode():
            output = self.model.encode_text(tokens, normalize=True).to(torch.float32)
        return l2_normalize(output[0].detach().cpu().numpy())

    def encode_image(self, image: str | Path | Image.Image) -> np.ndarray:
        tensor = self.preprocess(load_image(image)).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            output = self.model.encode_image(tensor, normalize=True).to(torch.float32)
        return l2_normalize(output.detach().cpu().numpy())


class ModelRegistry:
    def __init__(self, config: SearchConfig = DEFAULT_CONFIG):
        self.config = config
        self._encoders: dict[str, BaseEncoder] = {}

    def get(self, model: str) -> BaseEncoder:
        name = normalize_model_name(model)
        if name not in self._encoders:
            if name == "beit3":
                self._encoders[name] = BEIT3Encoder(self.config)
            elif name == "jina":
                self._encoders[name] = JinaOmniEncoder(
                    self.config.jina_model_name,
                    self.config,
                )
            elif name == "pe":
                self._encoders[name] = OpenCLIPEncoder(
                    self.config.pe_model_name,
                    self.config.models[name].vector_size,
                    self.config,
                )
        return self._encoders[name]

    def encode_text(self, text: str, model: str = "beit3") -> np.ndarray:
        return self.get(model).encode_text(text)

    def encode_image(self, image: str | Path | Image.Image, model: str = "beit3") -> np.ndarray:
        return self.get(model).encode_image(image)
