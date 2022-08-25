#include <M5Stack.h>
#include <Wire.h>

int gas_din=26;
int gas_ain=36;
uint16_t ad_value;
uint16_t di_value;

void setupMQ135()
{
  Wire.begin();

  pinMode(gas_din,INPUT);
  pinMode(gas_ain,INPUT);
}

void measureMQ135()
{
  ad_value=analogRead(gas_ain);
  di_value=digitalRead(gas_din);
}

void displayMQ135()
{
  M5.Lcd.setTextSize(2);
  M5.Lcd.setCursor(10, 10);

  if(di_value==LOW)
    {
      M5.Lcd.printf("Gas leakage!\n");
      M5.Lcd.printf("ad_value: %.2f V\n", ad_value*3.3/1024);
    }
  else
    {
      M5.Lcd.printf("Gas not leak\n");
    }
}
