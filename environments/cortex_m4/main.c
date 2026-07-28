#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "mlkem_native.h"
#include "notrandombytes.h"

#define REG32(address) (*(volatile uint32_t *)(address))
#define RCC_AHB1ENR REG32(0x40023830U)
#define RCC_APB1ENR REG32(0x40023840U)
#define GPIOC_MODER REG32(0x40020800U)
#define GPIOC_AFRH REG32(0x40020824U)
#define UART4_SR REG32(0x40004C00U)
#define UART4_DR REG32(0x40004C04U)
#define UART4_BRR REG32(0x40004C08U)
#define UART4_CR1 REG32(0x40004C0CU)

#define RESULT_PASS 0x4D4C4B50U /* ASCII: MLKP */
#define RESULT_FAIL 0x4D4C4B46U /* ASCII: MLKF */

volatile uint32_t mlkem_result_marker __attribute__((section(".result_marker")));

static void uart_init(void)
{
  RCC_AHB1ENR |= (1U << 2);
  RCC_APB1ENR |= (1U << 19);
  GPIOC_MODER = (GPIOC_MODER & ~(3U << 20)) | (2U << 20);
  GPIOC_AFRH = (GPIOC_AFRH & ~(15U << 8)) | (8U << 8);
  UART4_BRR = 0x8BU;
  UART4_CR1 = (1U << 13) | (1U << 3);
}

static void put_char(char value)
{
  while ((UART4_SR & (1U << 7)) == 0U) { }
  UART4_DR = (uint32_t)value;
}

static void put_text(const char *text)
{
  while (*text != '\0') { put_char(*text++); }
}

static void put_u32(uint32_t value)
{
  char digits[10];
  unsigned int count = 0;
  if (value == 0U) { put_char('0'); return; }
  while (value != 0U) { digits[count++] = (char)('0' + (value % 10U)); value /= 10U; }
  while (count != 0U) { put_char(digits[--count]); }
}

int main(void)
{
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
  uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
  uint8_t key_a[CRYPTO_BYTES];
  uint8_t key_b[CRYPTO_BYTES];
  int keygen_rc;
  int enc_rc;
  int dec_rc;

  uart_init();
  put_text("MLKEM-RENODE-START\r\n");
  randombytes_reset(); /* Deliberately deterministic: test harness only. */
  keygen_rc = crypto_kem_keypair(pk, sk);
  enc_rc = crypto_kem_enc(ct, key_b, pk);
  dec_rc = crypto_kem_dec(key_a, ct, sk);
  put_text("VERIFY,");
  if (keygen_rc == 0 && enc_rc == 0 && dec_rc == 0 && memcmp(key_a, key_b, CRYPTO_BYTES) == 0) {
    mlkem_result_marker = RESULT_PASS;
    put_text("PASS");
  } else {
    mlkem_result_marker = RESULT_FAIL;
    put_text("FAIL");
  }
  put_text("\r\nMLKEM-RENODE-END\r\n");
  for (;;) { __asm volatile ("wfi"); }
}
