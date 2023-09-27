/*
* Created by David Yount 9/27/23
* Function i2c_transfer taken from https://github.com/pradeepa-s/beagleboneblack.git by pradeepa-s.
* Code inspired by Derek Molloy's book Exploring BeagleBone Black. Explore that here: https://github.com/derekmolloy/exploringBB.git
* This code was written as a bare-bones single file application for reading sensor data from an Si7021-A20.
* It serves as an educational piece on linux i2c transfer. In the future I plan to wrap this functionality in a c++ class.
*/

#include <sys/stat.h>
#include <stdio.h>
#include <time.h>
#include <string.h>
#include <fcntl.h>
#include <sys/types.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>

/* This code is meant to funciton on the Beaglebone Black running headless debian. 
*  This will not work for other architectures as is.
*  I2C Bus 2 is presumed. Your linux distro or board may use other bus numbers.
*  For the BBB, wiring is the following: SDA is connected to P9 19 and SCL is connected to P9 20
*  VCC is connected to 3.3V and all ground connections lead to the same ground pin on the BB.
*/

//Todo: Use better debugging, not prints.

static int file_handle; //File Scope.
static int i2c_transfer(const char* cmd, const size_t cmd_length, char* read_buf, const size_t read_length); //Prototype because we're not using a header file.

int main(void)
{
    const char filename[] = "/dev/i2c-2";
	const int addr = 0x40; //Hardware address of the device.

	file_handle = open(filename, O_RDWR);
    if (ioctl(file_handle, I2C_SLAVE, addr) < 0)
	{
		close(file_handle);
        return 0;
		printf("IOCTL Failed\n");
	}

    const char electronic_id_2[2] = {0xFC, 0xC9}; //This is a command that tells the sensor to read back its ID.
	char id_val[4];

    //First I2C transfer is done manually for educational purposes.
    size_t transfer_length = write(file_handle, electronic_id_2, 2); //Tells the device where we want to read
    if (transfer_length == 2) //If write is successfull
	{
		transfer_length = read(file_handle, id_val, 4); //Begin read
		if (transfer_length == 4) //If read is successfull
		{
			printf("Read is a success\n");
            for (int i = 0; i < 4; i++)
            {
                printf("0x%x ",(int)id_val[i]);
            }
            printf("\n Readback complete \n");
		}
        else
        {
            printf("Read unsucessfull\n");
        } 
	}
    if(id_val[0] == 0x15)
    {
        printf("ID is correct\n");
    }
    else
    {
        printf("ID Is incorrect\n");
    }
    //Manual I2C Transfer ends here. From now on we use the function i2c_transfer.

    const char measure_rel_humidity = 0xE5;
	const char read_temperature = 0xE0;
	unsigned short temperature, humidity;
    for(int i = 0; i < 50; i++)
    {
        // Read humidity
        if(i2c_transfer(&measure_rel_humidity, sizeof(measure_rel_humidity), (char*)&humidity, sizeof(humidity)) != 0)
        {
            printf("Read humidity failed\n");
        }

        // Read temperature
        if(i2c_transfer(&read_temperature, sizeof(read_temperature), (char*)&temperature, sizeof(temperature)) != 0)
        {
            printf("Read temp failed\n");
        }

        //Endiness shift
        temperature = ((temperature & 0x00FF) << 8) | ((temperature & 0xFF00) >> 8);
        humidity = ((humidity & 0x00FF) << 8) | ((humidity & 0xFF00) >> 8);

        //Transform temp code to Celsius
        temperature = (175.72 * temperature)/65536 - 46.85;
        printf("Temperature is: %hu Sample: %i\n",temperature,i);
        sleep(1);
    }
    close(file_handle);
    return 0;
}

// -------------------------------

int i2c_transfer(const char* cmd, const size_t cmd_length, char* read_buf, const size_t read_length)
{
	size_t transfer_length = write(file_handle, cmd, cmd_length);

	if (transfer_length == cmd_length)
	{
		transfer_length = read(file_handle, read_buf, read_length);

		if (transfer_length == read_length)
		{
			return 0;
		}
	}

	return 1;
}