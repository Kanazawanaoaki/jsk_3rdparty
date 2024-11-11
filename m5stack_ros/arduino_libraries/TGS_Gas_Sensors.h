// You can use M5STACK or M5ATOM_S3
#define M5ATOM_S3
/* #define M5STACK */

#include <m5stack_ros.h>
#include <Wire.h>

#if defined(M5STACK)
  int gas_din=26;
  int gas_ain=36;
#elif defined(M5ATOM_S3)
  int gas_din=2;
  int gas_ain=1;
#endif

uint16_t analog_value;
uint16_t digital_value;

void setupTGSSensors()
{
  Wire.begin();

  pinMode(gas_din,INPUT);
  pinMode(gas_ain,INPUT);
}

void measureTGSSensors()
{
  analog_value=analogRead(gas_ain);
  digital_value=digitalRead(gas_din);
}

void displayTGSSensors()
{
  M5.Lcd.setTextSize(2);
  M5.Lcd.setCursor(10, 10);

  M5.Lcd.printf("analog_value: %04d\n", analog_value);
  M5.Lcd.printf("digital_value: %01d\n", digital_value);
}
