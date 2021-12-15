BEGIN_STATUS = "Программа не запущена"
WAIT_FOR_COMPLETED_STATUS = "Ожидание обработки записей"
DOWNLOADING_RECORDS_STATUS = "Скачивание записей с zoom"
UPLOADING_RECORDS_STATUS = "Загрузка записи на youtube"
MOVE_TO_PLAYLIST_STATUS = "Перемещение записи в плэйлист"
DELETING_FILES_STATUS = "Удаление файлов"
QUOTA_EXCEEDED = "Превышено допустимое число загрузок в день"
NO_TOKENS = "Токены отсутствуют\n" \
            "Для создания перейдите по ссылке\n"
INVALID_TOKENS = "Требуется обновление инвалидизированных токенов\n" \
                 "Для обновления перейдите по ссылке\n"
NEW_TOKENS = "Токены обновлены"
END_STATUS = "Записи успешно опубликованы"


class Message:

    def __init__(self, status=BEGIN_STATUS, progress=(None, None), end=False, link=(None, None)):

        self.status = status
        self.link = link
        self.progress = progress
        self.end = end
