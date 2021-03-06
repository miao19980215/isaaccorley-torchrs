import os
from collections import namedtuple
from typing import Dict

import h5py
import torch

from torchrs.transforms import Compose, ToTensor


class ZueriCrop(torch.utils.data.Dataset):
    """ ZueriCrop dataset from 'Crop mapping from image time series:
    deep learning with multi-scale label hierarchies', Turkoglu et al. (2021)
    https://arxiv.org/abs/2102.08820

    'We provide a new, publicly available crop classification dataset ZueriCrop, equipped
    with a tree-structured label hierarchy. ZueriCrop covers a 50 km × 48 km area
    in the Swiss cantons of Zurich and Thurgau. It contains 28,000 Sentinel-2 image
    patches of size 24 pixels × 24 pixels, each observed 71 times over a period of
    52 weeks; 48 agricultural land cover classes; and 116,000 individual agricultural fields.'

    """
    ZueriCropClass = namedtuple("ZueriCropClass", ["id", "label", "level1", "level2", "level3", "description"])
    classes = [
        ZueriCropClass(0, "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"),
        ZueriCropClass(1, "SummerBarley", "Vegetation", "Field crops", "SmallGrainCereal", "summer barley"),
        ZueriCropClass(2, "WinterBarley", "Vegetation", "Field crops", "SmallGrainCereal", "Winter barley"),
        ZueriCropClass(3, "Oat", "Vegetation", "Field crops", "SmallGrainCereal", "oats"),
        ZueriCropClass(4, "Wheat", "Vegetation", "Field crops", "SmallGrainCereal", "triticale"),
        ZueriCropClass(5, "Grain", "Vegetation", "Field crops", "SmallGrainCereal", "mixed fodder cereals"),
        ZueriCropClass(6, "Wheat", "Vegetation", "Field crops", "SmallGrainCereal", "Feed wheat according to the list of varieties swiss granum"),
        ZueriCropClass(7, "Maize", "Vegetation", "Field crops", "LargeGrainCereal", "grain maize"),
        ZueriCropClass(8, "EinkornWheat", "Vegetation", "Field crops", "SmallGrainCereal", "wild emmer, einkorn wheat"),
        ZueriCropClass(9, "SummerWheat", "Vegetation", "Field crops", "SmallGrainCereal", "summer wheat"),
        ZueriCropClass(10, "WinterWheat", "Vegetation", "Field crops", "SmallGrainCereal", "Winter wheat (without forage wheat of the variety list swiss granum),"),
        ZueriCropClass(11, "Rye", "Vegetation", "Field crops", "SmallGrainCereal", "rye"),
        ZueriCropClass(12, "Grain", "Vegetation", "Field crops", "SmallGrainCereal", "mixed cereals for bread production"),
        ZueriCropClass(13, "Spelt", "Vegetation", "Field crops", "SmallGrainCereal", "Spelt"),
        ZueriCropClass(14, "Maize", "Vegetation", "Field crops", "LargeGrainCereal", "maize for seed production (by contract),"),
        ZueriCropClass(15, "Maize", "Vegetation", "Field crops", "LargeGrainCereal", "Mads d'ensilage et mads vert"),
        ZueriCropClass(16, "Sugar_beets", "Vegetation", "Field crops", "BroadLeafRowCrop", "Sugar beets"),
        ZueriCropClass(17, "Beets", "Vegetation", "Field crops", "BroadLeafRowCrop", "fodder beet"),
        ZueriCropClass(18, "Potatoes", "Vegetation", "Field crops", "BroadLeafRowCrop", "potatoes"),
        ZueriCropClass(19, "Potatoes", "Vegetation", "Field crops", "BroadLeafRowCrop", "potatoes for planting (by contract),"),
        ZueriCropClass(20, "SummerRapeseed", "Vegetation", "Field crops", "BroadLeafRowCrop", "summer rapeseed for oil production"),
        ZueriCropClass(21, "WinterRapeseed", "Vegetation", "Field crops", "BroadLeafRowCrop", "Winter rape for cooking oil"),
        ZueriCropClass(22, "Soy", "Vegetation", "Field crops", "BroadLeafRowCrop", "soy"),
        ZueriCropClass(23, "Sunflowers", "Vegetation", "Field crops", "BroadLeafRowCrop", "Sunflowers"),
        ZueriCropClass(24, "Linen", "Vegetation", "Field crops", "BroadLeafRowCrop", "flax"),
        ZueriCropClass(25, "Hemp", "Vegetation", "Field crops", "BroadLeafRowCrop", "hemp"),
        ZueriCropClass(26, "Field bean", "Vegetation", "Field crops", "BroadLeafRowCrop", "Field beans for animal feed"),
        ZueriCropClass(27, "Peas", "Vegetation", "Field crops", "BroadLeafRowCrop", "protein peas for animal fodder"),
        ZueriCropClass(28, "Lupine", "Vegetation", "Field crops", "BroadLeafRowCrop", "lupine for fodder"),
        ZueriCropClass(29, "Pumpkin", "Vegetation", "Field crops", "VegetableCrop", "oil pumpkins"),
        ZueriCropClass(30, "Tobacco", "Vegetation", "Field crops", "BroadLeafRowCrop", "tobacco"),
        ZueriCropClass(31, "Sorghum", "Vegetation", "Field crops", "LargeGrainCereal", "millet"),
        ZueriCropClass(32, "Grain", "Vegetation", "Field crops", "SmallGrainCereal", "Ensiled grain"),
        ZueriCropClass(33, "Linen", "Vegetation", "Field crops", "BroadLeafRowCrop", "false flax (camelina sativa),"),
        ZueriCropClass(34, "Vegetables", "Vegetation", "Field crops", "VegetableCrop", "Annual free-range vegetables, without canned vegetables"),
        ZueriCropClass(35, "Vegetables", "Vegetation", "Field crops", "VegetableCrop", "Ground-canned vegetables"),
        ZueriCropClass(36, "Chicory", "Vegetation", "Field crops", "VegetableCrop", "chicory roots"),
        ZueriCropClass(37, "Buckwheat", "Vegetation", "Field crops", "SmallGrainCereal", "buckwheat"),
        ZueriCropClass(38, "Sorghum", "Vegetation", "Field crops", "LargeGrainCereal", "sorghum"),
        ZueriCropClass(39, "Berries", "Vegetation", "Special crops", "Berries", "Annual berries (e.g., strawberries),"),
        ZueriCropClass(40, "Unknown", "Vegetation", "Special crops", "Unknown", "single-year regrowing ressources (Kenaf and others),"),
        ZueriCropClass(41, "Unknown", "Vegetation", "Special crops", "Unknown", "Annual spice and medicinal plants"),
        ZueriCropClass(42, "Unknown", "Vegetation", "Special crops", "Unknown", "Annual horticultural outdoor crops (flowers, turf etc.),"),
        ZueriCropClass(43, "Biodiversity encouragement area", "Vegetation", "Grassland", "BiodiversityArea", "Conservation headlands"),
        ZueriCropClass(44, "Fallow", "Vegetation", "Special crops", "Fallow", "fallow"),
        ZueriCropClass(45, "Fallow", "Vegetation", "Special crops", "Fallow", "rotational set-aside"),
        ZueriCropClass(46, "Unknown", "Vegetation", "Grassland", "Meadow", "Hem on arable land"),
        ZueriCropClass(47, "Unknown", "Vegetation", "Special crops", "Unknown", "Poppy"),
        ZueriCropClass(48, "Unknown", "Vegetation", "Special crops", "Unknown", "safflower"),
        ZueriCropClass(49, "Unknown", "Vegetation", "Field crops", "CropMix", "lentils"),
        ZueriCropClass(50, "MixedCrop", "Vegetation", "Field crops", "CropMix", "Mixtures of field beans, protein peas and lupines for animal feed with cereals, at least 30% legume content at harvest"),
        ZueriCropClass(51, "Biodiversity encouragement area", "Vegetation", "Grassland", "BiodiversityArea", "Bloom strips for pollinators and other beneficials"),
        ZueriCropClass(52, "Mustard", "Vegetation", "Field crops", "BroadLeafRowCrop", "mustard"),
        ZueriCropClass(53, "WinterRapeseed", "Vegetation", "Field crops", "BroadLeafRowCrop", "Winter rape as a renewable raw material"),
        ZueriCropClass(54, "Sunflowers", "Vegetation", "Field crops", "BroadLeafRowCrop", "Sunflowers as regrowing ressource"),
        ZueriCropClass(55, "Unknown", "Bare soil", "Unknown", "Unknown", "open arable land, eligible for subsidies (region-specific biodiversity area),"),
        ZueriCropClass(56, "Unknown", "Bare soil", "Unknown", "Unknown", "Other open arable land, eligible"),
        ZueriCropClass(57, "Unknown", "Bare soil", "Unknown", "Unknown", "Other open arable land, not eligible"),
        ZueriCropClass(58, "Meadow", "Vegetation", "Grassland", "Meadow", "Art meadows (without pastures),"),
        ZueriCropClass(59, "Meadow", "Vegetation", "Grassland", "Meadow", "Other artificial meadow, eligible (eg pork pasture, poultry pasture),"),
        ZueriCropClass(60, "Meadow", "Vegetation", "Grassland", "Meadow", "Extensively used meadows (without pastures),"),
        ZueriCropClass(61, "Meadow", "Vegetation", "Grassland", "Meadow", "Little intensively used meadows (without pastures),"),
        ZueriCropClass(62, "Meadow", "Vegetation", "Grassland", "Meadow", "Other permanent pastures (without pastures),"),
        ZueriCropClass(63, "Pasture", "Vegetation", "Grassland", "Pasture", "Pastures (pastures, other pastures without summer pastures),"),
        ZueriCropClass(64, "Pasture", "Vegetation", "Grassland", "Pasture", "Extensively used pastures"),
        ZueriCropClass(65, "Pasture", "Vegetation", "Grassland", "Pasture", "Forest pastures (without wooded area),"),
        ZueriCropClass(66, "Meadow", "Vegetation", "Grassland", "Meadow", "Hay meadows in the summering area, other meadows"),
        ZueriCropClass(67, "Meadow", "Vegetation", "Grassland", "Meadow", "Hay meadows in the summering area, type extensively used meadow"),
        ZueriCropClass(68, "Pasture", "Vegetation", "Grassland", "Pasture", "Forest pastures (without wooded area),"),
        ZueriCropClass(69, "Legumes", "Vegetation", "Field crops", "BroadLeafRowCrop", "fodder legumes (Fabaceae), for seed production (by contract),"),
        ZueriCropClass(70, "Unknown", "Vegetation", "Grassland", "Unknown", "fodder grasses for seed production (by contract),"),
        ZueriCropClass(71, "Meadow", "Vegetation", "Grassland", "Meadow", "Riverside meadows along rivers (without pastures),"),
        ZueriCropClass(72, "Unknown", "Vegetation", "Grassland", "BiodiversityArea", "Other green area (permanent green area),, entitled to contributions"),
        ZueriCropClass(73, "Unknown", "Vegetation", "Grassland", "Unknown", "Remaining green area (permanent green areas),, not eligible"),
        ZueriCropClass(74, "Vines", "Vegetation", "Orchards", "OrchardCrop", "vines"),
        ZueriCropClass(75, "Apples", "Vegetation", "Orchards", "OrchardCrop", "Fruit plants (apples),"),
        ZueriCropClass(76, "Pears", "Vegetation", "Orchards", "OrchardCrop", "Fruit plants (pears),"),
        ZueriCropClass(77, "StoneFruit", "Vegetation", "Orchards", "OrchardCrop", "Fruit plants (Steinobs),"),
        ZueriCropClass(78, "Berries", "Vegetation", "Special crops", "Berries", "Perennial berries"),
        ZueriCropClass(79, "Unknown", "Vegetation", "Special crops", "Unknown", "Perennial spice and medicinal plants"),
        ZueriCropClass(80, "Unknown", "Vegetation", "Special crops", "Unknown", "Perennial renewable resources (miscanthus, etc.),"),
        ZueriCropClass(81, "Hops", "Vegetation", "Orchards", "OrchardCrop", "hop"),
        ZueriCropClass(82, "Unknown", "Vegetation", "Special crops", "Unknown", "rhubarb"),
        ZueriCropClass(83, "Unknown", "Vegetation", "Special crops", "Unknown", "asparagus"),
        ZueriCropClass(84, "TreeCrop", "Vegetation", "Orchards", "TreeCrop", "Christmas trees"),
        ZueriCropClass(85, "TreeCrop", "Vegetation", "Orchards", "TreeCrop", "Nursery of forest plants outside the forest zone"),
        ZueriCropClass(86, "Unknown", "Vegetation", "Special crops", "Unknown", "Ornamental shrubs, ornamental shrubs and ornamental shrubs"),
        ZueriCropClass(87, "Unknown", "Vegetation", "Special crops", "Unknown", "Other nurseries (roses, fruits, etc.),"),
        ZueriCropClass(88, "Vines", "Vegetation", "Orchards", "OrchardCrop", "Vineyards with natural biodiversity"),
        ZueriCropClass(89, "Unknown", "Vegetation", "Special crops", "Unknown", "Truffle plants (in production),"),
        ZueriCropClass(90, "Unknown", "Vegetation", "Special crops", "Unknown", "Mulberry trees (feeding silkworms),"),
        ZueriCropClass(91, "Chestnut", "Vegetation", "Orchards", "OrchardCrop", "Cultivated selven (chestnut trees),"),
        ZueriCropClass(92, "Unknown", "Vegetation", "Special crops", "Unknown", "Perennial horticultural outdoor crops (not in the greenhouse),"),
        ZueriCropClass(93, "Vines", "Vegetation", "Orchards", "OrchardCrop", "vines nursery"),
        ZueriCropClass(94, "Unknown", "Vegetation", "Special crops", "Unknown", "Other fruit plants (kiwis, elderberries, etc.),"),
        ZueriCropClass(95, "Vines", "Vegetation", "Orchards", "OrchardCrop", "vines (region-specific biodiversity area),"),
        ZueriCropClass(96, "Unknown", "Vegetation", "Special crops", "BiodiversityArea", "Other areas with permanent crops, eligible"),
        ZueriCropClass(97, "Unknown", "Vegetation", "Special crops", "Unknown", "Other areas with permanent crops, not eligible"),
        ZueriCropClass(98, "Vegetables", "Infrastructure", "Unknown", "Greenhouse", "Vegetable crops in greenhouses with solid foundations"),
        ZueriCropClass(99, "Special cultures", "Infrastructure", "Unknown", "Greenhouse", "Other specialized crops in greenhouses with solid foundations"),
        ZueriCropClass(100, "Special cultures", "Infrastructure", "Unknown", "Greenhouse", "Horticultural crops in greenhouses with solid foundations"),
        ZueriCropClass(101, "Vegetables", "Unknown", "Unknown", "ProtectedCultivation", "Vegetable crops in protected cultivation without firm foundations"),
        ZueriCropClass(102, "Special cultures", "Unknown", "Unknown", "ProtectedCultivation", "Other special crops in protected cultivation without firm foundations"),
        ZueriCropClass(103, "Special cultures", "Unknown", "Unknown", "ProtectedCultivation", "Horticultural crops in protected cultivation without firm foundations"),
        ZueriCropClass(104, "Special cultures", "Unknown", "Unknown", "ProtectedCultivation", "Other crops in protected cultivation without a firm foundation"),
        ZueriCropClass(105, "Unknown", "Infrastructure", "Unknown", "Unknown", "other cultures in protected cultivation with solid foundation),"),
        ZueriCropClass(106, "Special cultures", "Unknown", "Unknown", "ProtectedCultivation", "Other crops in protected cultivation without firm foundations, not eligible"),
        ZueriCropClass(107, "Unknown", "Vegetation", "Special crops", "Unknown", "Scattering areas in the LN"),
        ZueriCropClass(108, "Hedge", "Vegetation", "Special crops", "Hedge", "Hedge, field and bank shrubs (with herbaceous area),"),
        ZueriCropClass(109, "Hedge", "Vegetation", "Special crops", "Hedge", "Hedgerow, field and bank shrubs (with buffer strips),"),
        ZueriCropClass(110, "Hedge", "Vegetation", "Special crops", "Hedge", "Hedgerow, field and bank shrubs (with buffer strips), (region-specific biodiversity production area),"),
        ZueriCropClass(111, "Multiple", "Undefined", "Unknown", "Unknown", "Other areas within the LN, entitled to contribute"),
        ZueriCropClass(112, "Multiple", "Undefined", "Unknown", "Unknown", "Other areas within the LN, not eligible"),
        ZueriCropClass(113, "Forest", "Vegetation", "Forest", "Forest", "Forest"),
        ZueriCropClass(114, "Multiple", "Vegetation", "Special crops", "Multiple", "Other unproductive areas (eg mulched areas, heavily weedy areas, hedges without buffer strips),"),
        ZueriCropClass(115, "Non agriculture", "Undefined", "Unknown", "Undefined", "Areas without main agricultural purpose (developed building land, playground, riding, camping, golf, air and military spaces"),
        ZueriCropClass(116, "Waters", "Undefined", "Unknown", "Unknown", "Ditches, ponds, ponds"),
        ZueriCropClass(117, "Non agriculture", "Infrastructure", "Unknown", "Unknown", "Ruderal areas, cairns and ramparts"),
        ZueriCropClass(118, "Multiple", "Infrastructure", "Unknown", "Unknown", "dry stone walls"),
        ZueriCropClass(119, "Unknown", "Bare soil", "Unknown", "Unknown", "non-asphalted, natural paths"),
        ZueriCropClass(120, "Biodiversity encouragement area", "Vegetation", "Grassland", "BiodiversityArea", "Region-specific biodiversity promotion areas"),
        ZueriCropClass(121, "Gardens", "Vegetation", "Special crops", "Gardens", "home gardens"),
        ZueriCropClass(122, "Unknown", "Infrastructure", "Unknown", "Unknown", "agricultural production in buildings (e.g. champignons, brussel sprouts),"),
        ZueriCropClass(123, "Pasture", "Vegetation", "Grassland", "Pasture", "Summer pastures"),
        ZueriCropClass(124, "Non agriculture", "Undefined", "Unknown", "Undefined", "Other areas outside the LN and SF")
    ]

    def __init__(
        self,
        root: str = ".data/zuericrop",
        transform: Compose = Compose([ToTensor()]),
    ):
        self.transform = transform
        self.f = h5py.File(os.path.join(root, "ZueriCrop.hdf5"), "r")

    def __len__(self) -> int:
        return self.f["data"].shape[0]

    def __getitem__(self, idx: int) -> Dict:
        x = self.f["data"][idx, ...]
        mask = self.f["gt"][idx, ...]
        instance_mask = self.f["gt_instance"][idx, ...]
        x, mask, instance_mask = self.transform([x, mask, instance_mask])
        return dict(x=x, mask=mask, instance_mask=instance_mask)
