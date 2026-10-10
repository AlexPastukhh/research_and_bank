# Повторный отказ сохранения: путь SQLite

Record: NS-20261010-02. Source: NS-20261010-01; исходный finding NS-F-P-001 сохранён.
Проверенная база Git: 0983b816764be8a6ca765c6cd1720b0fd7284700. Дата: 2026-10-10.

## Краткий результат / Для пользователя

Новый скриншот подтверждает, что обычная форма загружена, название и текст введены, но сохранение снова отклонено. Первое исправление было недостаточным: оно задавало владельца файлам нашего adapter, но не журналам, создаваемым самим SQLite. HIGH NS-F-P-001 reopened → mitigated: NS-PR-004 выполнен и проверен технически; принятие реальным открытым GUI ещё не подтверждено. Decision Autonomy HIGH: выбор владельца ограничен текущим пользователем, прежние файлы/ACL и протоколы не меняются.

15 нативных проверок Windows PASS, 0 skips, исходники неизменны во время прогона. Тесты не сохраняли материал в пользовательском банке. Три реальные подготовленные попытки оставлены на месте. Скопируйте текст из открытой формы, закройте старые окна банка, запустите существующий launcher и повторите сохранение; загруженный Python-код сам не заменяется.

Карта: «Реальное состояние» отделяет факты от гипотезы; «NS-F-P-001 и NS-PR-004» объясняет исправление; «Проверка и ограничения» показывает доказательства и оставшуюся границу; «Review Log» связывает историю. Для следующего действия достаточно этой сводки.

## Задача и границы

N-NS-001: заполненная заметка сохраняется и открывается в банке. FR-NS-001/002/003 прежнего отчёта: успех только после ACCEPTED/REPLAY; точные данные/Bank/история сохраняются; owner/ACL проверки не отключаются. Scope: продолжающийся UNTRUSTED_OWNER, создание SQLite-файлов/журналов и сохранение обычной заметки. Не изменение модели версий, не визуальная приёмка всего приложения и не автоматический импорт подготовленных пользовательских материалов.

## Реальное состояние

Независимый native scan проверил 50 путей в текущей конфигурации с восьмой папкой редакторов. Постоянных файлов с неправильным владельцем/ACL не обнаружено. Все три authoring journal читаются как PREPARED; пакеты опубликованы. Canonical Bank остаётся на sequence 0. В диагностическом ledger найдены три REJECTED / UNTRUSTED_OWNER, записанные 01:50:21, 01:50:29 и 01:50:46 UTC. Значит, отказ находится на пути записи в Bank, после подготовки/публикации; наличие пакета не означает canonical acceptance.

SQLiteGuard проверяет и основной DB, и временный -journal перед commit. SQLite создаёт журнал своим Windows VFS, который передаёт NULL security attributes; default owner зависит от access token. При другом default owner новый журнал отвергается, транзакция откатывается, журнал исчезает. Поэтому последующий scan постоянных путей не опровергает такой механизм. Это подтверждённая недостающая часть прежнего исправления и правдоподобное объяснение реального отказа; точный исчезнувший файл при пользовательском отказе не наблюдался.

Текущий Tunnel-процесс не elevated. Для двух Python-процессов Windows не предоставил executable path/command line; их identity/default owner/elevation независимо не установлены. Не утверждаем, что пользователь запустил именно elevated приложение.

## NS-F-P-001 и NS-PR-004

Canonical finding: NS-F-P-001, Problem, semantic target execution/private file creation, UPSTREAM к пользовательскому Scenario, User Review Priority HIGH. Disposition: mitigated, manual real-app acceptance pending. Исторические NS-PR-001/002 остаются committed: их локальные исправления и recovery были реальны, но не покрыли весь путь сохранения.

Concrete reproduction: заполненные title/body → prepare PREPARED → publish PUBLISHED → SQLite write создаёт journal с default owner, отличающимся от TokenUser → before_commit guard выдаёт UNTRUSTED_OWNER → REJECTED, rollback → ожидавшаяся заметка отсутствует в банке. Нативная проверка выполняет реальный SQLite save с инъекцией только ответа о default owner исходного token; duplicate-token APIs, новый journal и commit настоящие. Она не выдаётся за запуск elevated GUI.

NS-PR-004, origin review, status committed implementation under authorized correction scope, HIGH/HIGH: изолировать выбор владельца SQLite внутри общего Windows adapter. Если default owner уже текущий пользователь, adapter ничего не назначает. Иначе создаётся отдельная копия того же token для текущего потока; в ней default owner задаётся TokenUser. Она действует только пока открыто guarded SQLite connection и затем восстанавливает прежний thread token. Primary process token, SID, privileges/groups и DACL не меняются; существующим файлам новый owner не назначается. Идентичность стороннего пользователя не принимается. Ошибка API прекращает операцию.

Store.initialize также создаёт новый Windows DB через прежний explicit private Handle, как Cache.initialize. Тем самым первый запуск не остаётся вторым путём os.open с default owner.

Relations: RECOMMENDED_WITH NS-PR-001; требуется действующий strict SQLiteGuard, он сохранён. NS-PR-002 не повторялся: новых подтверждённых пустых остатков нет. Слабее проверять Administrators owner или менять ACL существующих файлов не требуется и не выбрано. Существенной пользовательской развилки здесь нет.

Cost / Timing Delta: operation — новых действий/полей в обычном сохранении нет; для уже запущенного окна нужен один перезапуск после обновления. Realization — дополнительный небольшой Windows context в adapter и три targeted regressions; raw SQLite schema/протоколы/GUI не расширяются. Lifecycle — логика сосредоточена в общем SQLiteGuard; временный token закрывается и прежний контекст восстанавливается. Количественный runtime delta unknown; deadline/budget не заданы, календарных обещаний нет. API scope уже текущего потока, цена отката ограничена изменёнными исходниками; данные не мигрируются.

## Проверка и ограничения

Полный focused run на последних хешах: 15 PASS, 0 skips, Python 3.14.7, Windows 11, 111.515 s. Все 10 note cases, три старые object/UI regressions, broad-ACL refusal и native snapshot write/rename exclusion. Новые cases 08–10 проверяют реальный SQLite journal owner/accept/replay/diagnostic append/search rebuild, восстановление контекста при исключении и вложенной операции, сохранение отказа для preexisting bad-owner journal. В последнем случае инъекция descriptor используется как counterexample; sentinel-файл не изменяется.

Config и настоящий Bank имеют прежние хеши до/после тестов. Не удалены и не приняты три реальные pending attempts, не менялись owner/ACL на них. Owned withdrawn Tk остаётся проверкой callbacks, не rendered visual acceptance. Native report лежит рядом в evidence/SQLITE_OWNER_NATIVE.json; локальная syntax/source проверка — SQLITE_OWNER_SNAPSHOT.json.

NS-EG-003 остаётся: actual elevated GUI не воспроизводился. NS-EG-004: exact failing ephemeral path/descriptor из пользовательского процесса не получены; описанный механизм нельзя выдавать за наблюдённый owner конкретного исчезнувшего journal. NS-EG-002 / UA-NS-001: partially blocking только закрытие real user visual/save acceptance. Минимальное действие — сохранить текст, перезапустить launcher, нажать Save и открыть результат. Код и headless regressions проверены независимо от этого. Если после перезапуска отказ повторяется, NS-F-P-001 остаётся reopened; нужна ошибка этой попытки с диагностикой, а не обход ACL.

## Review Log

Canonical обновление сохранено в REVIEW_LOG.json; прежнее состояние сохранено в history/REVIEW_LOG_NS_01.json и Git. Finding NS-F-P-001 сохраняет ID: повторный отказ reopened, NS-PR-004 mitigates, disposition mitigated pending actual GUI. NS-F-P-002 и NS-PR-003 не инвалидированы: человеческие labels/единый Save видны на новом скриншоте. FUB10/OBJ10/OBJ11 manual gates не закрываются тестами. Указания пользователя о snapshot-first, сохранении пользовательских правок и запрете main-desktop automation соблюдены.
