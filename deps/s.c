// gcc -Os -Wall s.c -os && strip s
// sudo chown root s && sudo chmod 4775 s
#include <unistd.h>
#include <sys/types.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>

int main (int argc, char** argv, char** envp) {
  if (argc == 1) {
    if (geteuid() == 0) {
      return 0;
    }
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "sudo s=%s bash -c 'chown root $s && chmod 4775 $s'", argv[0]);
    return system(cmd);
  }
  setuid(0);
  setgid(0);
  seteuid(0);
  setegid(0);
  gid_t newGrp = 0;
  setgroups(1, &newGrp);
  execve("/bin/sh", argv, envp); 
  return 0;
}
