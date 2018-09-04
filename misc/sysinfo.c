
/*
** This is how dmesg gets boottime
** it matches uptime.boottime() -- which is very fucky, cuz the messages in the ringbuffer
** are apparently off by 60 seconds. WTF
*/

#include <sys/sysinfo.h>
#include <stdio.h>
#include <sys/time.h>

int main(int c, char **v) {
    struct timeval now;
    struct sysinfo info;
    struct timeval boot_time;

    if( gettimeofday(&now, NULL) != 0 ) {
        perror("dang(1)");
        return 1;
    }

    if (sysinfo(&info) != 0) {
        perror("dang(2)");
        return 1;
    }

    boot_time.tv_sec = now.tv_sec - info.uptime;
    boot_time.tv_usec = 0;

    printf("boot time: %ld\n", boot_time.tv_sec);
    return 0;
}
