python -m esptool ^
-b 460800 ^
--before default_reset ^
--after hard_reset ^
--chip esp32s3 ^
write_flash ^
--flash_mode dio ^
--flash_freq 80m ^
--flash_size detect ^
	0x0000   bootloader_CP.bin ^
	0x8000   partition-table_8Mb.bin ^
	0x10000  ..\Launcher\build\m5stack.esp32.m5stack_stamp_s3\Launcher.ino.bin