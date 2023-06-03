# Mapping internal data / REST endpoints
This table helps to define which Solis REST API endpoints provide which information used for monitoring.

| fieldKey                 | fieldType | Unit | REST endpoint  | API                          |
|--------------------------|-----------|------|----------------|------------------------------|
| AC_Current               | float     | A    | inverterDetail | (iAc1+iAc2+iAc3)/3           |                         
| AC_Frequency             | float     | Hz   | inverterDetail | fac                          |
| AC_Power                 | float     | W    | inverterDetail | pac                          |
| AC_Voltage               | float     | V    | inverterDetail | (uAc1+uAc2+uAc3)/3           |                         
| Annual_Energy_Used       | float     | kWh  | inverterYear   | energy - gridSellEnergy      |                         
| Annual_Generation        | float     | kWh  | inverterYear   | energy                       |
| Battery_Charge_Percent   | float     |      |                |                              |                         
| Consumption_Energy       | float     | kWh  | inverterDetail | homeLoadTotalEnergy          |                         
| Consumption_Power        | float     | W    | inverterDetail | familyLoadPower              |                         
| DC_Current1              | float     | A    | inverterDetail | iPv1                         |
| DC_Current2              | float     | A    | inverterDetail | iPv2                         |
| DC_Current3              | float     | A    | inverterDetail | iPv3                         |
| DC_Current4              | float     | A    | inverterDetail | iPv4                         |
| DC_Power_PV1             | float     | W    | inverterDetail | pow1                         |
| DC_Power_PV2             | float     | W    | inverterDetail | pow2                         |
| DC_Power_PV3             | float     | W    | inverterDetail | pow3                         |
| DC_Power_PV4             | float     | W    | inverterDetail | pow4                         |
| DC_Voltage_PV1           | float     | V    | inverterDetail | uPv1                         |
| DC_Voltage_PV2           | float     | V    | inverterDetail | uPv2                         |
| DC_Voltage_PV3           | float     | V    | inverterDetail | uPv3                         |
| DC_Voltage_PV4           | float     | V    | inverterDetail | uPv4                         |
| Daily_Energy_Used        | float     | kWh  | inverterDetail | eToday - gridSellTodayEnergy |                         
| Daily_Generation         | float     | kWh  | inverterDetail | eToday                       |
| Generation_Last_Month    | float     | kWh  | inverterMonth  | energy                       |                         
| Inverter_Temperature     | float     | °C   | inverterDetail | inverterTemperature          |
| Monthly_Energy_Used      | float     | kWh  | inverterMonth  | energy - gridSellEnergy      |                         
| Monthly_Generation       | float     | kWh  | inverterDetail | eMonth                       |
| Power_Grid_Total_Power   | float     | W    | inverterDetail | pSum                         |                         
| Total_Energy_Purchased   | float     | kWh  | inverterDetail | gridPurchasedTotalEnergy     | 
| Total_Generation         | float     | kWh  | inverterDetail | eTotal                       |     
| Total_On_grid_Generation | float     | kWh  | inverterDetail | gridSellTotalEnergy          |      
| updateDate               | integer   |      | inverterDetail | dataTimestamp                |            
