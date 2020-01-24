#include <stdio.h>
#include <errno.h>
#include <fcntl.h>                          // for 'open()'
#include <unistd.h>                         // for 'close()'

void dispAudio(char* buf, int len) {
    for (int i=0;i<len;i++) {
        printf("%d ",buf[i]);
    }
    printf("\n");
}

int main() {

    //int fd = open("/dev/media0",O_RDONLY);
    int fd = open("/dev/snd/controlC1",O_RDONLY);
    if (fd < 1) {
        perror("error");
        return 1;
    }

    printf("opened, reading..\n");

    char buf[100] = {'\0'};
    int num = 0;
    while ((num = read(fd,buf,100)) > 0) {
        dispAudio(buf,num);
    }
    close(fd);


    return 0;
}
