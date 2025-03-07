from enum import Enum

import numpy as np


class LossType(Enum):
    CAT = "cat"
    NON_CAT = "non_cat"


cat_share = 0.33
size = 100000

loss_types = np.random.choice(
    [LossType.CAT.value, LossType.NON_CAT.value],
    size=size,
    p=[cat_share, 1 - cat_share],
)
print(loss_types.tolist().count("cat") / len(loss_types.tolist()))
