
const int N = 10;

int hrBuf[N];
int gasBuf[N];
float tempBuf[N];

int idx = 0;
bool filled = false;

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < N; i++) {
    hrBuf[i] = 0;
    gasBuf[i] = 0;
    tempBuf[i] = 0.0;
  }
}

void loop() {
  hrBuf[idx]  = analogRead(A0);
  gasBuf[idx] = analogRead(A1);
  tempBuf[idx] = 36.5 + (analogRead(A2) * 0.01);
  idx = (idx + 1) % N;
  if (idx == 0) filled = true;
  int count = filled ? N : idx;

  long hrSum = 0;
  long gasSum = 0;
  float tempSum = 0.0;

  for (int i = 0; i < count; i++) {
    hrSum += hrBuf[i];
    gasSum += gasBuf[i];
    tempSum += tempBuf[i];
  }
  int heartrate = hrSum / count;
  int gaslevel  = gasSum / count;
  float temp    = tempSum / count;

  Serial.print(heartrate);
  Serial.print(",");
  Serial.print(gaslevel);
  Serial.print(",");
  Serial.println(temp, 2);

  delay(1000);
}
