#include <stdint.h>

extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

int main(void);

void Reset_Handler(void)
{
  uint32_t *source = &_sidata;
  uint32_t *destination = &_sdata;
  while (destination < &_edata) { *destination++ = *source++; }
  for (destination = &_sbss; destination < &_ebss; ++destination) { *destination = 0U; }
  (void)main();
  for (;;) { __asm volatile ("wfi"); }
}

__attribute__((section(".isr_vector")))
void (*const vector_table[])(void) = {
  (void (*)(void))&_estack, Reset_Handler,
};
