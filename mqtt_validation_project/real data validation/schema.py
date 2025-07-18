# Pandera pandas API’sini direkt kullanmak üzere güncel import:
import pandera.pandas as pa
from pandera import Column, Check

# Katı Kurallar:
# strict=True: CSV'de şemada olmayan hiçbir sütun olamaz.
# nullable=False (varsayılan): Hiçbir hücre boş olamaz.
# Timestamp artık bir index değil, doğrulanması gereken bir sütun.

schema = pa.DataFrameSchema(
    {
        "Timestamp": Column(pa.DateTime),
        "A_ACR_Mot.PV": Column(float, Check.in_range(0, 0.005)),
        "A_ACR_Mot.SV": Column(float, Check.in_range(0, 20)),
        "A_ACR_Mot.TV": Column(float, Check.in_range(20, 50)),
        "A_ACR_Pmp.PV": Column(float, Check.in_range(0, 0.005)),
        "A_ACR_Pmp.SV": Column(float, Check.in_range(0, 65)),
        "A_ACR_Pmp.TV": Column(float, Check.in_range(25, 45)),
        "A_Pres.PV": Column(float, Check.in_range(0, 60)),
        "A_Temp.PV": Column(float, Check.in_range(20, 50)),
        "Barometer": Column(float, Check.in_range(1000, 1020)),
        "Temperature": Column(float, Check.in_range(20, 30)),
    },
    coerce=True,
    strict=True
)
