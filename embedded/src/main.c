// pico sdk
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

//protobuf
#include <pb_encode.h>
#include <pb_decode.h>
#include "protos/definitions.pb.h"

int main() {
    stdio_init_all();

    while (true) {
        sleep_ms(1000);
    }
}
