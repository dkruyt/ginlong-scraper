# Mapping internal data / REST endpoints
This table helps to define which Solis REST API endpoints provide which information used for monitoring.

| fieldKey                   | fieldType    | REST endpoint | API                      |
|----------------------------|--------------|---------------|--------------------------|
| AC_Current                 | float        |               |                          |                         
| AC_Frequency               | float        |               | fac                      |
| AC_Power                   | float        |               | pac                      |
| AC_Voltage                 | float        |               |                          |                         
| Annual_Energy_Used         | float        |               |                          |                         
| Annual_Generation          | float        |               | eYear                    |
| Battery_Charge_Percent     | float        |               |                          |                         
| Consumption_Energy         | float        |               |                          |                         
| Consumption_Power          | float        |               |                          |                         
| DC_Current1                | float        |               | iPv1                     |
| DC_Current2                | float        |               | iPv2                     |
| DC_Current3                | float        |               | iPv3                     |
| DC_Current4                | float        |               | iPv4                     |
| DC_Power_PV1               | float        |               | uPv1*iPv1                |
| DC_Power_PV2               | float        |               | uPv2*iPv2                |
| DC_Power_PV3               | float        |               | uPv3*iPv3                |
| DC_Power_PV4               | float        |               | uPv4*iPv4                |
| DC_Voltage_PV1             | float        |               | uPv1                     |
| DC_Voltage_PV2             | float        |               | uPv2                     |
| DC_Voltage_PV3             | float        |               | uPv3                     |
| DC_Voltage_PV4             | float        |               | uPv4                     |
| Daily_Energy_Used          | float        |               |                          |                         
| Daily_Generation           | float        |               | eToday                   |
| Generation_Last_Month      | float        |               |                          |                         
| Inverter_Temperature       | float        |               | inverterTemperature      |
| Monthly_Energy_Used        | float        |               |                          |                         
| Monthly_Generation         | float        |               | eMonth                   |
| Power_Grid_Total_Power     | float        |               |                          |                         
| Total_Energy_Purchased     | float        |               | gridPurchasedTotalEnergy | 
| Total_Generation           | float        |               | eTotal                   |     
| Total_On_grid_Generation   | float        |               | gridSellTotalEnergy      |      
| updateDate                 | integer      |               | dataTimestamp            |            