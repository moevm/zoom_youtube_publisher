BEGIN_STATUS = "Программа не запущена"
WAIT_FOR_COMPLETED_STATUS = "Ожидание обработки записей"
DOWNLOADING_RECORDS_STATUS = "Скачивание записей с zoom"
UPLOADING_RECORDS_STATUS = "Загрузка записи на youtube"
MOVE_TO_PLAYLIST_STATUS = "Перемещение записи в плэйлист"
DELETING_FILES_STATUS = "Удаление файлов"
QUOTA_EXCEEDED = "Превышено допустимое число загрузок в день"
END_STATUS = "Записи успешно опубликованы"


class Message:

    def __init__(self, status=BEGIN_STATUS, progress=(None, None), end=False):

        self.status = status
        self.progress = progress
        self.end = end
