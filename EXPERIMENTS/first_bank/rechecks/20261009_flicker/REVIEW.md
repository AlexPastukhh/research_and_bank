# Мигание Bank и доступность редакторов — UIF-20261009-01

## Краткий результат / Для пользователя

Периодический observe использовал foreground busy/status и отключал все кнопки. UIF-F-P-001 исправлен. Нижние панели редакторов вытеснялись расширяющимся главным frame; UIF-F-P-002 исправлен технически.10local/11Windows focused checks PASS,0skips, источники неизменны на протяжении финальных прогонов. Подтверждение исправленного вида пользователем остаётся pending.

HIGH: UIF-F-P-003 → UIF-PR-003 pending: реальный индекс поиска пуст (0bytes), owner Administrators вместо текущего пользователя. Его origin неизвестен. Попытка guarded сохранения/восстановления отказана UNTRUSTED_OWNER до любой замены. Поиск пока не принят; нужны owner/context evidence и отдельное безопасное исправление. Autonomy MEDIUM, только search/FUB10 частично блокированы. HIGH: UIF-F-P-002 → UIF-PR-002 committed: кнопки теперь размещены в основной области; следующий шаг — пользовательский перезапуск/видимая проверка.

В отчёте: «Причина и исправление» объясняет изменение обработки observe; «Что проверено» показывает реальные контрпримеры очереди и закрытия; «Незакрытый поиск» описывает отказ и неизменность Bank; «Следующее действие» задаёт минимальную визуальную проверку. Все canonical IDs/Proposals находятся в [Review Log](REVIEW_LOG.json).

## Причина и исправление

Два пользовательских снимка показывают disabled controls + «Выполняется: observe» и enabled controls + «OK / BANK_OBSERVED». Код запускает observe раз в2секунды через обычный submit. Новый путь использует прежний единственный Bridge без model.begin/set_busy/status для опроса. Действие пользователя захватывается неизменяемо и выполняется после опроса; повторное нажатие при уже принятом foreground request не запускает дубль. Закрытие ожидает опрос и уже принятую операцию. Sync notice меняется только при изменении текста.

Editor/safeguard controls теперь в tools_area внутри основного outer до расширяющегося pane. Пять object действий разбиты на две строки; chooser уменьшен. Main desktop GUI не открывался и не автоматизировался.

## Что проверено

[Локальные10](evidence/LOCAL_605d33cbd86c4f7abadd46e7d969de59.json), [Windows11](evidence/NATIVE_933690cbe33d47a9ab012dc66e50307c.json): несколько тихих опросов; отсутствие busy/status repaint и потери pinned detail; фактический Bridge/threads с максимумом1worker; captured args и один queued click; search click во время observe; доступность входа в object form; close idle/queued save; реальные existing external save/pinned selection/rebuild/read-only search и notice recovery. Windows дополнительно создаёт собственный withdrawn Tk window и проверяет pack-parent/order, grid/width. Это технический proof, не человеческая визуальная приёмка. Ошибка первого локального test fixture и его report сохранены.

## Незакрытый поиск

[Наблюдение реального кэша](ACTUAL_CACHE_OBSERVATION.json):0bytes, owner O:BA, owner_matches_current_user false. [Fresh HOST](HOST_PREFLIGHT.json) и последующий readback показывают тот же Bank SHA. Config/Bank/индекс не изменялись при отказанной repair попытке. Политика владельца/ACL не ослаблена, права ОС не менялись. Изолированный native fresh setup успешно строит пустой индекс32768bytes, поэтому механизм появления существующего invalid cache ещё не установлен. Не объявляем его повреждением canonical Bank или подтверждённой ошибкой конкретного процесса.

## Следующее действие

Перезапустить обычный launch_bank.cmd, проверить отсутствие периодического отключения кнопок и наличие Entity/Collection/targeted Annotation/edit controls. UA UIF-UA-001. FUB10/OBJ10/OBJ11 не закрывать по одному скриншоту или headless PASS. UIF-PR-003 pending: отдельно установить GUI ownership/context и безопасно восстановить derived index без обхода guards; search acceptance остаётся открыта. Подробные dispositions/limits/costs и Review Log сохранены в единственной canonical JSON-записи.
