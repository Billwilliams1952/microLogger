
/*
ADCReadData.cpp - The routines to capture data and return the results to Python
  
Copyright 2020  <billwilliams2718@gmail.com>

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the 
Free Software Foundation, either version 3 of the License, or (at your 
option) any later version.

This program is distributed in the hope that it will be useful,but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for 
more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <https://www.gnu.org/licenses/>.

gcc -shared -o ADCReadData.so -lwiringPi -fPIC ADCReadData.c

*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <wiringPi.h>
#include <wiringPiSPI.h>
#include <ctime>
#include <time.h>
#include <chrono>
#include <sys/time.h>
#include <math.h>

using namespace std;

#define DEF_ADC_CS      3   // WiringPi pin numbers!!!!
#define DEF_SYNC_PWRDN  2   // WiringPi pin numbers!!!!
#define DEF_ADC_RDY     0   // WiringPi pin numbers!!!!
#define MAX_MUX_CHANNELS 8

class CPPClass
{
public:

    int             fd, CHANNEL = 0, MUX_SETTLE_USEC = 270, NumMuxes;
    FILE *          filePtr = nullptr;
    unsigned char   Gain        = 1;
    double          VRef        = 2.5;
    unsigned char   buffer[4];                    // Four for RDATA
    int             ADC_CS, SYNC_PWRDN, ADC_RDY;
    unsigned char   MuxReg[MAX_MUX_CHANNELS];     // Up to 8 channels
    double          VoltsPerBit  = 0.0;
    double          Readings[MAX_MUX_CHANNELS];   // Up to 8 channels
    double          LastReadings[MAX_MUX_CHANNELS];
    double          TimeStamp = 0.0, SampleTime, TimeStampEnd, 
                    DeltaMeasTime = 0,
                    OldMeasTime, NewMeasTime;
    bool            Restart = true, PauseRestart = false, Logging = true;
    int             RPIBoardRev = 1;

    CPPClass()  {
    }
    
    void Init() {
        ADC_CS = DEF_ADC_CS;
        SYNC_PWRDN = DEF_SYNC_PWRDN;
        ADC_RDY = DEF_ADC_RDY;
        
        fd = wiringPiSetup ();
        printf("Initialized wiringPiSetup: result = %d\n",fd);
        fd = wiringPiSPISetupMode(CHANNEL,1500000,1);  // Mode 1
        printf("Initialized wiringPiSPISetupMode: result = %d\n",fd); 
        
        //pinMode (SHUTDOWN, INPUT);
        pinMode (ADC_RDY, INPUT);
        
        pinMode (SYNC_PWRDN, OUTPUT);
        digitalWrite (SYNC_PWRDN, HIGH); 
        
        pinMode (ADC_CS, OUTPUT);
        digitalWrite (ADC_CS, HIGH); 
        
        SetGain(Gain);
        
        usleep(1000);
        
        // Setup internal Sample Frequency to 15,000 SPS
        digitalWrite (ADC_CS, LOW);
        usleep(10);
        buffer[0] = 0x53; buffer[1] = 0x00; buffer[2] = 0xE0; 
        fd = wiringPiSPIDataRW(CHANNEL, buffer, 3);
        digitalWrite (ADC_CS, HIGH);
        printf("ADC Internal sampling rate set to 15,000 SPS\n");
        
        sleep(1);
        
        OffsetAndGainCal();
        
        for ( int i = 0; i < MAX_MUX_CHANNELS; i++ ) {
            LastReadings[i] = 0.0;
        }
        
        RPIBoardRev = piBoardRev();
        printf("RPI Board Revision Number: %d\n",RPIBoardRev);
        /* This returns the board revision of the Raspberry Pi. 
         * It will be either 1 or 2. Some of the BCM_GPIO pins changed 
         * number and function when moving from board revision 1 to 2, 
         * so if you are using BCM_GPIO pin numbers, then you need to be
         * aware of the differences.
         */
        
        printf("Init Done...\n");
    }
    
    int ReturnRPIBoardNumber() { return RPIBoardRev; }
    
    void OffsetAndGainCal () {
        digitalWrite (ADC_CS, LOW);
        usleep(10);
        buffer[0] = 0xF0;
        fd = wiringPiSPIDataRW(CHANNEL, buffer, 1);
        digitalWrite (ADC_CS, HIGH);
        sleep(1);
        printf("Offset and Gain Calibration complete\n");
    }
    
    void SetVRef(double _VRef) {
        VRef = _VRef;
        VoltsPerBit = 2.0 * VRef / (Gain * 8388607.0);
    }
    
    // Only allows up to 8 channels right now until I can figure out how
    // to pass lists back and forth
    // Terminate the list with a 0xFF -------
    void SetMuxChannels(unsigned char A, unsigned char B, unsigned char C, 
                        unsigned char D, unsigned char E, unsigned char F, 
                        unsigned char G, unsigned char H) {
        MuxReg[0] = A;
        MuxReg[1] = B;
        MuxReg[2] = C;
        MuxReg[3] = D;
        MuxReg[4] = E;
        MuxReg[5] = F;
        MuxReg[6] = G;
        MuxReg[7] = H;
        
        NumMuxes = 0;
        for (int i=0; i < MAX_MUX_CHANNELS; i++) {
            if ( MuxReg[i] != 0xFF ) NumMuxes++;
            else break;
        }
    }
    
    void SetSampleTime(double _SampleTime) {
        SampleTime = _SampleTime;
    }
    
    void SetGain(unsigned char _Gain) {
        Gain = _Gain;
        VoltsPerBit = 2.0 * VRef / (Gain * 8388607.0);
        
        buffer[0] = 0x52; buffer[1] = 0x00; 
        switch ( Gain ) {
            case 1: buffer[2] = 0; break;
            case 2: buffer[2] = 1; break;
            case 4: buffer[2] = 2; break;
            case 8: buffer[2] = 3; break;
            case 16: buffer[2] = 4; break;
            case 32: buffer[2] = 5; break;
            case 64: buffer[2] = 6; break;
            case 128: buffer[2] = 7; break;
            default: buffer[2] = 1; break;
        }
        
        digitalWrite (ADC_CS, LOW);
        usleep(10);       
        fd = wiringPiSPIDataRW(CHANNEL, buffer, 3);   
        digitalWrite (ADC_CS, HIGH); 
        usleep(10000);
    }
    
    double timesec () {                                                                 
        struct timeval tv;                                                                 
        gettimeofday(&tv, NULL);                                                           
        return  (double)tv.tv_sec + (double)tv.tv_usec * 1.0e-6;                                               
    }
    
    void ReadData() {
        // The main data gathering routine. Loop through the MuxInputs
        // until a 0xFF is found
        int val;

        TimeStamp = timesec();

        for(int i = 0; i < NumMuxes; i++) {
            // Set MUX Channel
            digitalWrite (ADC_CS, LOW);
            //usleep(5);
            buffer[0] = 0x51; buffer[1] = 0x00; buffer[2] = MuxReg[i]; 
            fd = wiringPiSPIDataRW(CHANNEL, buffer, 3);  
            digitalWrite (ADC_CS, HIGH); 
            
            // Should we include a minimum delay to ensure the Mux has
            // settled by now??
            usleep(MUX_SETTLE_USEC);
            
            /* Begin internal 'Glitch' loop */
            double last = fabs(LastReadings[i]);
            int j = 0;
            for ( ; j < 2; j++ ) {
            
                digitalWrite (SYNC_PWRDN, LOW);
                usleep(5);
                digitalWrite (SYNC_PWRDN, HIGH); 
                
                // Wait for new conversion to be complete...
                while ( digitalRead(ADC_RDY) == HIGH ) ; // loop forever 
                
                if ( i == 0 ) {
                    if ( j == 0 )
                        OldMeasTime = NewMeasTime;
                    NewMeasTime = timesec();   // Time measurement starts
                }
            
                digitalWrite (ADC_CS, LOW);
                usleep(2);
                buffer[0] = 0x01;
                fd = wiringPiSPIDataRW(CHANNEL, buffer, 1);
                usleep(1);
                //// Now read the data....
                fd = wiringPiSPIDataRW(CHANNEL, buffer, 3);
                
                digitalWrite(ADC_CS,HIGH); 
                
                val = (buffer[0] << 16) | (buffer[1] << 8) | buffer[2];
                Readings[i] = ((-(val & 0x800000) + (val & 0x7FFFFF)) * VoltsPerBit);
                
                // TRY TO DETECT BAD DATA GLITCHES....
                // If abs(value) is not within previous abs(value) by say 10% then
                // read again... if still out - assume its OK? and continue
                double current = fabs(Readings[i]);
                
                if ( (current < last * 1.05) && (current > last * 0.95) )
                    j = 2;
                //else
                //    printf("Retry glitch\n");
                
            } 
            LastReadings[i] = Readings[i];        
        }
        
        if ( Restart ) {    //     # Start again at time = 0
            DeltaMeasTime = 0;
            OldMeasTime = NewMeasTime;
            Restart = false;
        } else {
            //if ( PauseRestart && Logging )  // THIS IS THE BUG???
            //    PauseRestart = false;
            //else
            DeltaMeasTime = DeltaMeasTime + NewMeasTime - OldMeasTime;
        }
        TimeStampEnd = timesec();
        //printf("HERE\n");
    }
    
    void ReadCurrentChannel() {
        int val;
        
        digitalWrite (SYNC_PWRDN, LOW);
        usleep(5);
        digitalWrite (SYNC_PWRDN, HIGH); 
        
        while ( digitalRead(ADC_RDY) == HIGH ) ; // loop forever 
    
        digitalWrite (ADC_CS, LOW);
        //usleep(10);
        buffer[0] = 0x01;
        fd = wiringPiSPIDataRW(CHANNEL, buffer, 1);
        //usleep(1);
        fd = wiringPiSPIDataRW(CHANNEL, buffer, 3);

        digitalWrite(ADC_CS,HIGH); 
        
        val = (buffer[0] << 16) | (buffer[1] << 8) | buffer[2];
        Readings[0] = ((-(val & 0x800000) + (val & 0x7FFFFF)) * VoltsPerBit);
    }
    
    double GetReading(int i) {
        return Readings[i];
    }
    
    double GetTimeStamp() {
        return TimeStamp;
    }
    
    double GetDeltaTime() {
        return TimeStampEnd - TimeStamp;
    }
    
    double GetRealDelay() {
        //printf("GetRealDelay = %0.4f\n",SampleTime - ( timesec() - TimeStamp ));
        if (TimeStamp == 0.0) return SampleTime;
        return SampleTime - ( timesec() - TimeStamp );
    }
    
    double GetUpdateTime() {
        //printf("DeltaMeasTime = %0.4f\n",DeltaMeasTime);
        return DeltaMeasTime;
    }
    
    void SetRestart() { Restart = true; }
    
    void SetPauseRestart() { PauseRestart = true; }

};

// For use with python:
extern "C" {
    CPPClass* CPPClass_py() { return new CPPClass(); }
    
    void Init(CPPClass* myClass) { myClass->Init(); }
    
    int ReturnRPIBoardNumber(CPPClass* myClass) { return myClass->ReturnRPIBoardNumber(); }
    
    void SetSampleTime(CPPClass* myClass,double SampleTime) { myClass->SetSampleTime(SampleTime); }    
    
    void SetRestart(CPPClass* myClass) { myClass->SetRestart(); }  
    
    void SetPauseRestart(CPPClass* myClass) { myClass->SetPauseRestart(); }  
    
    double GetReading(CPPClass* myClass, int i) { return myClass->GetReading(i); }
    
    double GetTimeStamp(CPPClass* myClass) { return myClass->GetTimeStamp(); }
    
    double GetDeltaTime(CPPClass* myClass) { return myClass->GetDeltaTime(); }
    
    double GetRealDelay(CPPClass* myClass) { return myClass->GetRealDelay(); }
    
    double GetUpdateTime(CPPClass* myClass) { return myClass->GetUpdateTime(); }
    
    void ReadData(CPPClass* myClass) { myClass->ReadData(); }
    
    void ReadCurrentChannel(CPPClass* myClass) { myClass->ReadCurrentChannel(); }
    
    void SetGain(CPPClass* myClass, unsigned char Gain) { myClass->SetGain(Gain); }
    
    void OffsetAndGainCal(CPPClass* myClass) { myClass->OffsetAndGainCal(); }
    
    void SetVRef(CPPClass* myClass, double VRef) { myClass->SetVRef(VRef); }
    
    void SetMuxChannels(CPPClass* myClass, unsigned char A, unsigned char B, 
                    unsigned char C, unsigned char D, unsigned char E, 
                    unsigned char F, unsigned char G, unsigned char H) {
        myClass->SetMuxChannels(A, B, C, D, E, F, G, H);
        return;
    }
    
}




