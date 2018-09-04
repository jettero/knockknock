/*
** dmesg may also get the boottime this way
** but this also matches uptime.boottime()
** ... even if we did this, we'd still be off by 60 seconds. WTF.
*/

#include <stdio.h>
#include <time.h>
#include <sys/time.h>

int main(int c, char **v) {
    struct timeval now;
    struct timeval boot_time;
    struct timeval lores_uptime;
    struct timespec hires_uptime;

    if( gettimeofday(&now, NULL) != 0 ) {
        perror("dang(1)");
        return 1;
    }

    if (clock_gettime(CLOCK_BOOTTIME, &hires_uptime) == 0 ) {
        // TIMESPEC_TO_TIMEVAL(&lores_uptime, &hires_uptime);
        // sys/time.h should have this macro,
        // ... it lives in /usr/include/x86_64-linux-gnu/sys/time.h
        // but it's still missing from sys/time.h
        // including linux/time.h makes everything awful, ... meh; this is all it does:
        lores_uptime.tv_sec  = hires_uptime.tv_sec;
        lores_uptime.tv_usec = hires_uptime.tv_nsec / 1000;

        timersub(&now, &lores_uptime, &boot_time);
        printf("boot time: %ld\n", boot_time.tv_sec);
    }

    return 1;
}
