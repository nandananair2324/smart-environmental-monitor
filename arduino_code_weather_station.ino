#include <LiquidCrystal.h>
#include <DHT.h>
#include <SoftwareSerial.h>

// Define LCD Pins (RS, E, D4, D5, D6, D7)
LiquidCrystal lcd(7, 8, 9, 10, 11, 12); // Connect LCD directly

// Define Sensors & Actuators
#define DHTPIN 2         
#define DHTTYPE DHT11    
#define LDR A1          
#define MQ135 A2        

#define GREEN_LED A3     // Green LED (Normal Condition)
#define YELLOW_LED A4     // Yellow LED (Warning)
#define RED_LED A5       // Red LED (Critical Alert)
#define BUZZER 6         // Buzzer
#define ESP_TX 3         // ESP8266 TX
#define ESP_RX 4         // ESP8266 RX

DHT dht(DHTPIN, DHTTYPE);
SoftwareSerial esp(ESP_TX, ESP_RX);

void setup() {
    Serial.begin(115200);
    esp.begin(9600);
    dht.begin();

    // Initialize LCD
    lcd.begin(16, 2);  // 16x2 LCD
    lcd.print("Env Monitor");  
    delay(2000);
    lcd.clear();

    pinMode(LDR, INPUT);
    pinMode(MQ135, INPUT);
    pinMode(GREEN_LED, OUTPUT);
    pinMode(YELLOW_LED, OUTPUT);
    pinMode(RED_LED, OUTPUT);
    pinMode(BUZZER, OUTPUT);

    Serial.println("Environmental Monitor Initialized");
}

void loop() {
    // Read Sensor Data
    float tempDHT = dht.readTemperature();
    float humDHT = dht.readHumidity();
    int lightIntensity = analogRead(LDR);
    int airQuality = analogRead(MQ135);

    // Display on LCD
    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print(tempDHT);
    lcd.print("C H:");
    lcd.print(humDHT);
    lcd.print("%");

    lcd.setCursor(0, 1);
    lcd.print("L:");
    lcd.print(lightIntensity);
    lcd.print(" AQ:");
    lcd.print(airQuality);

    // Send Data to ESP8266 for Remote Transmission
    String data = String(tempDHT) + "," + String(humDHT) + "," + 
                  String(lightIntensity) + "," + String(airQuality);
    esp.println(data);
        Serial.println(data);

    // LED & Buzzer Warning System
    if (tempDHT > 40 || airQuality > 800) { 
        digitalWrite(GREEN_LED, LOW);
        digitalWrite(YELLOW_LED, LOW);
        digitalWrite(RED_LED, HIGH);
        digitalWrite(BUZZER, HIGH);
        Serial.println("❌ CRITICAL ALERT!");
    } 
    else if (tempDHT > 35 && tempDHT < 40 || airQuality > 600) { 
        digitalWrite(GREEN_LED, LOW);
        digitalWrite(YELLOW_LED, HIGH);
        digitalWrite(RED_LED, LOW);
        digitalWrite(BUZZER, LOW);
        Serial.println("⚠ WARNING!");
    } 
    else { 
        digitalWrite(GREEN_LED, HIGH);
        digitalWrite(YELLOW_LED, LOW);
        digitalWrite(RED_LED, LOW);
        digitalWrite(BUZZER, LOW);
        Serial.println("✅ Environment Normal.");
    }

    delay(2000);
}