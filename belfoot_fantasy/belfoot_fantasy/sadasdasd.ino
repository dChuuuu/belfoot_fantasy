#include <Wire.h>
#include <Eeprom24C32_64.h>
#include <SoftwareSerial.h>
#include <DallasTemperature.h>
#include <FastLED.h>
#include <Time.h>

#define DS1307_I2C_ADDRESS 0x68
#define EEPROM_ADDRESS  0x57
#define ONE_WIRE_BUS 6
#define NUM_LEDS 74 //  Number of LED controlled
#define COLOR_ORDER GRB  // Define color order for your strip
#define LED_PIN 3 // Data pin for led comunication
#define BRIGHTNESS  255



SoftwareSerial bt=SoftwareSerial(4,5);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensor(&oneWire);
CRGB leds[NUM_LEDS]; // Define LEDs strip


//Что-то про часы пока не разобрался
byte decToBcd(byte val){return ( (val/10*16) + (val%10) );}
byte bcdToDec(byte val){return ( (val/16*10) + (val%16) );}
//Что-то про часы пока не разобрался


static Eeprom24C32_64 eeprom(EEPROM_ADDRESS);



byte second, minute, hour,hrs, dayOfWeek, dayOfMonth, month, year;
byte temp,minute1;
boolean aktpoint=1,point,first=0;
int stime;

byte digits[12][18] = {{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0}, //digit 0
                       {0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0}, //digit 1
                       {0,0,0,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1}, //digit 2
                       {0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1}, //digit 3
                       {1,1,1,0,0,0,0,0,1,1,1,1,1,1,0,0,1,1}, //digit 4
                       {1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,1,1,1}, //digit 5
                       {1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1}, //digit 6
                       {0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0}, //digit 7
                       {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}, //digit 8
                       {1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1}, //digit 9
                       {1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1}, // digit *C
                       {1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,0,0}}; //digit C

bool Dot = true;  //Dot state
bool DST = false; //DST state
bool TempShow = false;
int last_digit = 0;
unsigned long last,lost;
int digit;

 //int ledColor = 0x991FFB; // Color used (in hex)
long ledColor = CRGB::Green; // Color used (in hex)
//long ledColor = CRGB::MediumVioletRed;
//Random colors i picked up
long ColorTable[17] = {
  CRGB::Amethyst,
  CRGB::Aqua,
  CRGB::Blue,
  CRGB::Chartreuse,
  CRGB::DarkGreen,
  CRGB::DarkMagenta,
  CRGB::DarkOrange,
  CRGB::DeepPink,
  CRGB::Fuchsia,
  CRGB::Gold,
  CRGB::GreenYellow,
  CRGB::LightCoral,
  CRGB::Tomato,
  CRGB::Salmon,
  CRGB::Red,
  CRGB::Orchid,
  CRGB::Green
};





void setup() {
  Serial.begin(9600);
  bt.begin(9600);
  eeprom.initialize();
  FastLED.addLeds<WS2812, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setBrightness(  BRIGHTNESS );
  Wire.begin();
  sensor.begin();
  sensor.setResolution(12);
  getDateDs1307(&second, &minute, &hour, &dayOfWeek, &dayOfMonth, &month, &year);
  //setDateDs1307(second,minute=4,hour=21,dayOfWeek,dayOfMonth,month,year);
}

// Convert time to array needet for display
void TimeToArray(){
  int cursor = 74; // last led number
  for(int i=1;i<=4;i++){
        if (digit != last_digit){

        //cylon();
        ledColor =  ColorTable[16];
        FastLED.show();
      }
      last_digit = digit;
    if (i==4){
    // Serial.print("Digit 4 is : ");Serial.print(digit);Serial.print(" ");

      cursor = 56;
       digit = minute%10;
      for(int k=0; k<=17;k++){
         //Serial.print(digits[digit][k]);
        if (digits[digit][k]== 1){leds[cursor]=ledColor;}
         else if (digits[digit][k]==0){leds[cursor]=0x000000;}
         //Serial.println(cursor);
         cursor ++;
        }

/*      if (digit != last_digit)
      {
        FastLED.show();
        //cylon();
        ledColor =  ColorTable[16];
      }
      last_digit = digit;
      */
      }
    else if (i==3){
      //Serial.print("Digit 3 is : ");Serial.print(digit);Serial.print(" ");

      cursor =38;
      int digit = minute/10;
      for(int k=0; k<=17;k++){
        // Serial.print(digits[digit][k]);
        if (digits[digit][k]== 1){leds[cursor]=ledColor;}
         else if (digits[digit][k]==0){leds[cursor]=0x000000;};
         cursor ++;
        };
      // Serial.println();
      }
    else if (i==2){
      // Serial.print("Digit 2 is : ");Serial.print(digit);Serial.print(" ");
      cursor =18;
      int digit = hour%10;
      for(int k=0; k<=17;k++){
        // Serial.print(digits[digit][k]);
        if (digits[digit][k]== 1){leds[cursor]=ledColor;}
         else if (digits[digit][k]==0){leds[cursor]=0x000000;};
         cursor ++;
        };
      // Serial.println();
      }
    else if (i==1){
      // Serial.print("Digit 1 is : ");Serial.print(digit);Serial.print(" ");
      cursor =0;
      int digit = hour/10;
      for(int k=0; k<=17;k++){
        // Serial.print(digits[digit][k]);
        if (digits[digit][k]== 1){leds[cursor]=ledColor;}
         else if (digits[digit][k]==0){leds[cursor]=0x000000;};
         cursor ++;
        };
      // Serial.println();
      }
    //Now /= 10;
  };
}
// coool effect function
void fadeall() { for(int i = 0; i < NUM_LEDS; i++) { leds[i].nscale8(250); } }



void cylon () {
  static uint8_t hue = 0;
  // First slide the led in one direction
  for(int i = 0; i < NUM_LEDS; i++) {
    // Set the i'th led to red
    leds[i] = CHSV(hue++, 255, 255);
    // Show the leds
    FastLED.show();
    // now that we've shown the leds, reset the i'th led to black
     //leds[i] = CRGB::Black;
    fadeall();
    // Wait a little bit before we loop around and do it again
    delay(10);
  }

  // Now go in the other direction.
  for(int i = (NUM_LEDS)-1; i >= 0; i--) {
    // Set the i'th led to red
    leds[i] = CHSV(hue++, 255, 255);
    // Show the leds
    FastLED.show();
    // now that we've shown the leds, reset the i'th led to black
    // leds[i] = CRGB::Black;
    fadeall();
    // Wait a little bit before we loop around and do it again
    delay(10);
  }
}

void changing(){
	for(byte k=0; k<=17;k++){
	}




}





String we;

void loop() {
  pointer();
    if(first==0){TimeToArray();cylon();first=1;}

    if(millis()-lost>30000){
      lost=millis();
      getDateDs1307(&second, &minute, &hour, &dayOfWeek, &dayOfMonth, &month, &year);  }

    if(minute1!=minute){
      TimeToArray();
      minute1=minute;
    }

//getDateDs1307(&second, &minute, &hour, &dayOfWeek, &dayOfMonth, &month, &year);
//sensor.requestTemperatures();
//temp=sensor.getTempCByIndex(0);


  if (bt.available() > 0) // пришли данные
  { aktpoint=0;
    we = char(bt.read());
      Serial.print(we); // вывод данных с переносом строки
      we="";
     }else{delay(30);aktpoint=1;}
/*
  while (Serial.available())
  {message += char(Serial.read());} //сохраняем строку от входящих сообщений

  if (!Serial.available())
  {if (message != "")
    { //если данные доступны
    Serial.println(message); //выводим данные
      message = ""; //очищаем данные
     }
    }




if (bt.available()){
  aktpoint=0;
  Serial.write(bt.read());
}else{delay(50);aktpoint=1;}
if(Serial.available()){
  bt.write(Serial.read());
  aktpoint=0;
}
*/











}








void pointer(){
  if(aktpoint==1){
    FastLED.show();
    if (millis()-last>500 && point==0){
      last=millis();
      leds[36]=ledColor;
      leds[37]=ledColor;
      point=1;
    }
    if (millis()-last>500 && point==1){
      last=millis();
      leds[36]=0x000000;
      leds[37]=0x000000;
      point=0;
    }   }
    else{
      leds[36]=0x000000;
      leds[37]=0x000000;}
}


void setDateDs1307(byte second, byte minute, byte hour, byte dayOfWeek, byte dayOfMonth, byte month, byte year) {
   Wire.beginTransmission(DS1307_I2C_ADDRESS);
   Wire.write(0);
   Wire.write(decToBcd(second));
   Wire.write(decToBcd(minute));
   Wire.write(decToBcd(hour));
   Wire.write(decToBcd(dayOfWeek));
   Wire.write(decToBcd(dayOfMonth));
   Wire.write(decToBcd(month));
   Wire.write(decToBcd(year));
   Wire.endTransmission();
}
void getDateDs1307(byte *second, byte *minute, byte *hour, byte *dayOfWeek, byte *dayOfMonth, byte *month, byte *year){
  Wire.beginTransmission(DS1307_I2C_ADDRESS);
  Wire.write(0);
  Wire.endTransmission();

  Wire.requestFrom(DS1307_I2C_ADDRESS, 7);

  *second     = bcdToDec(Wire.read() & 0x7f);
  *minute     = bcdToDec(Wire.read());
  *hour       = bcdToDec(Wire.read() & 0x3f);
  *dayOfWeek  = bcdToDec(Wire.read());
  *dayOfMonth = bcdToDec(Wire.read());
  *month      = bcdToDec(Wire.read());
  *year       = bcdToDec(Wire.read());
}
void zapis (){
  Wire.beginTransmission(DS1307_I2C_ADDRESS);
  Wire.write(0);
  Wire.endTransmission();
  Wire.requestFrom(DS1307_I2C_ADDRESS, 7);

  second     = bcdToDec(Wire.read() & 0x7f);
  minute     = bcdToDec(Wire.read());
  hour       = bcdToDec(Wire.read() & 0x3f);
  dayOfWeek  = bcdToDec(Wire.read());
  dayOfMonth = bcdToDec(Wire.read());
  month      = bcdToDec(Wire.read());
  year       = bcdToDec(Wire.read());
}
