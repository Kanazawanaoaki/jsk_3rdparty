#include <MQ_135_Gas_Sensor.h>
#include <m5stack_ros.h>
#include <std_msgs/UInt16.h>
#include <std_msgs/Float32.h>

std_msgs::Float32 tgs_gas_analog_msg;
std_msgs::UInt16 tgs_gas_digital_msg;
ros::Publisher tgs_gas_analog_pub("tgs_gas_analog", &tgs_gas_analog_msg);
ros::Publisher tgs_gas_digital_pub("tgs_gas_digital", &tgs_gas_digital_msg);

void setup()
{
  setupM5stackROS("M5Stack ROS TGS_Gas_Sensor");
  setupMQ135();

  nh.advertise(tgs_gas_analog_pub);
  nh.advertise(tgs_gas_digital_pub);
//  Serial.begin(115200);
}
void loop()
{
  measureMQ135();
//  if(di_value==LOW)
//  {
//    Serial.println("Gas leakage");
//    Serial.print("ad_value:");
//    Serial.print(ad_value*3.3/1024);
//    Serial.println("V");
//  }
//  else
//  {
//    Serial.println("Gas not leak");
//  }
  displayMQ135();

  tgs_gas_analog_msg.data = ad_value;
  tgs_gas_digital_msg.data = di_value;
  tgs_gas_analog_pub.publish(&tgs_gas_analog_msg);
  tgs_gas_digital_pub.publish(&tgs_gas_digital_msg);
  nh.spinOnce();

  delay(500);
}
