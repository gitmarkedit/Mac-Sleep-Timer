-- Таймер сна для macOS
-- Позволяет выбрать время (15м, 30м, 45м, 1ч, 1.5ч, 2ч, 3ч или свое значение)
-- и переводит Mac в режим сна.

set presetOptions to {"15 минут", "30 минут", "45 минут", "1 час (60 мин)", "1.5 часа (90 мин)", "2 часа (120 мин)", "3 часа (180 мин)", "Ввести вручную (в минутах)..."}

set userSelection to choose from list presetOptions with prompt "Через сколько перевести Mac в режим сна?" default items {"30 минут"} OK button name "Запустить" cancel button name "Отмена" with title "Таймер сна"

if userSelection is false then
	return
end if

set selectedItem to item 1 of userSelection
set totalMinutes to 30

if selectedItem is "15 минут" then
	set totalMinutes to 15
else if selectedItem is "30 минут" then
	set totalMinutes to 30
else if selectedItem is "45 минут" then
	set totalMinutes to 45
else if selectedItem is "1 час (60 мин)" then
	set totalMinutes to 60
else if selectedItem is "1.5 часа (90 мин)" then
	set totalMinutes to 90
else if selectedItem is "2 часа (120 мин)" then
	set totalMinutes to 120
else if selectedItem is "3 часа (180 мин)" then
	set totalMinutes to 180
else if selectedItem is "Ввести вручную (в минутах)..." then
	set customDialog to display dialog "Введите время в минутах (например: 30 или 60):" default answer "30" buttons {"Отмена", "Запустить"} default button "Запустить" cancel button "Отмена" with title "Таймер сна"
	set rawText to text returned of customDialog
	try
		set totalMinutes to rawText as number
		if totalMinutes ≤ 0 then error
	on error
		display alert "Ошибка" message "Пожалуйста, введите положительное число минут." as critical
		return
	end try
end if

set totalSeconds to (totalMinutes * 60) as integer

display notification ("Mac перейдет в спящий режим через " & totalMinutes & " мин.") with title "Таймер сна" subtitle "Таймер запущен (закройте приложение в Dock для отмены)"

if totalSeconds > 15 then
	delay (totalSeconds - 15)
	activate
	try
		display dialog "Mac перейдет в режим сна через 15 секунд..." buttons {"Отменить", "Усыпить сейчас"} default button "Усыпить сейчас" cancel button "Отменить" giving up after 15 with title "Таймер сна" with icon caution
	on error number -128
		display notification "Таймер сна отменен пользователем." with title "Таймер сна"
		return
	end try
else
	delay totalSeconds
end if

do shell script "pmset sleepnow"
