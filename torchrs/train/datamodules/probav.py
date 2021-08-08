from typing import Optional

import torch
import torchvision.transforms as T

from torchrs.datasets.utils import dataset_split
from torchrs.train.datamodules import BaseDataModule
from torchrs.transforms import ToTensor, ToDtype
from torchrs.datasets import PROBAV


class PROBAVDataModule(BaseDataModule):

    def __init__(
        self,
        root: str = ".data/probav",
        band: str = "RED",
        lr_transform: T.Compose = T.Compose([ToTensor(), ToDtype(torch.float32)]),
        hr_transform: T.Compose = T.Compose([ToTensor(), ToDtype(torch.float32)]),
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.root = root
        self.band = band
        self.lr_transform = lr_transform
        self.hr_transform = hr_transform

    def setup(self, stage: Optional[str] = None):
        train_dataset = PROBAV(
            root=self.root, split="train", band=self.band, lr_transform=self.lr_transform, hr_transform=self.hr_transform
        )
        self.train_dataset, self.val_dataset = dataset_split(train_dataset, val_pct=self.val_split)
        self.test_dataset = PROBAV(
            root=self.root, split="test", band=self.band, lr_transform=self.lr_transform, hr_transform=self.hr_transform
        )
