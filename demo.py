import intake
src=intake.open_sdmx_sources()
ecb=src.ECB
exr=ecb.EXR(FREQ='Q', CURRENCY='USD',
    CURRENCY_DENOM='EUR', startPeriod='2019')

