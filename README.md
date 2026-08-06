# CleanDrive Bot (multi-user, v4.0, Google Drive backend)

Чистит метаданные (EXIF/GPS/IPTC/XMP) из фото и файлов без потери качества и
складывает результат на **Google Drive** пользователя. Каждый подключает
свой Диск через OAuth. По итогу — публичная ссылка на папку (доступ по
ссылке, без входа в аккаунт у получателя) и честный отчёт: что загрузилось,
что нет.

## Почему Google, а не Яндекс
Публичная ссылка на **папку** в Яндекс.Диске требует от получателя войти в
свой Яндекс-аккаунт (это подтверждённое ограничение платформы, не
настраивается). У Google Drive такого ограничения нет — "anyone with the
link" работает по-настоящему без авторизации получателя.

## Как это работает
1. `/start` → кнопка «Подключить Google Drive» → пользователь логинится **на
   странице Google** и разрешает доступ. Пароль бот не видит никогда.
2. Пользователь шлёт фото/файлы (можно альбомом, или несколько файлов подряд
   — они соберутся в один пакет автоматически).
3. Бот показывает, что нашёл (в т.ч. ⚠️ GPS), и спрашивает:
   «Очистить метаданные» / «Загрузить как есть» (можно отменить кнопкой).
4. «Обезличить имена?» → при «Да» файлы станут 001, 002, 003…
5. Бот спрашивает имя папки, грузит файлы по одному (если один не
   загрузился — остальные всё равно продолжают грузиться), присылает точный
   отчёт по именам и ссылку на папку — доступна кому угодно по ссылке, без
   необходимости входить в Google-аккаунт.
6. Успешно загруженные исходные сообщения удаляются из чата.

## Настройка

### 1. Google Cloud
- **https://console.cloud.google.com/** → создать/выбрать проект
- Включить **Google Drive API**: поиск "Drive API" → Enable
  (https://console.cloud.google.com/apis/library)
- **Google Auth Platform** (в интерфейсе Google Cloud — раньше называлось
  "OAuth consent screen"):
  - Заполнить Branding: App name, support email, developer contact email
  - User Type: **External**
  - **Audience** → добавить свою почту в Test users (пока не опубликовано),
    либо сразу нажать **Publish App** (перевести в статус **In Production**)
    — для scope `drive.file` это разрешено без верификации Google, так как
    scope несенситивный
- **Credentials → Create Credentials → OAuth client ID**
  (https://console.cloud.google.com/apis/credentials)
  - Application type: **Web application**
  - Authorized redirect URIs → `https://<твой-render-домен>.onrender.com/oauth/callback`
  - Сохрани **Client ID** и **Client secret** (можно скачать `client_secret.json`)

### 2. Supabase
```sql
create table if not exists disk_users (
  telegram_id bigint primary key,
  access_token text,
  refresh_token text,
  created_at timestamptz default now()
);
```
(если таблица уже существует с прошлой версии на Яндексе — можно оставить
как есть, схема не меняется)

### 3. Telegram
Токен бота у @BotFather → `BOT_TOKEN`.

### 4. Render (Web Service, Docker)
Задеплой репозиторий (Dockerfile нужен ради `exiftool`).
Environment variables:
- `BOT_TOKEN`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `OAUTH_REDIRECT_URI` = `https://<твой-домен>.onrender.com/oauth/callback`
  (ровно как в Google Cloud Console)
- `SUPABASE_URL`
- `SUPABASE_KEY`

`PORT` Render прокидывает сам; на нём поднимается OAuth-callback и `/health`.

## Команды
- `/start` — подключить Диск / инструкция
- `/logout` — удалить токены из базы (доступ можно также отозвать на
  myaccount.google.com/permissions)

## Нюансы
- Присылай как **Файл/Document**, иначе Telegram сам пережмёт «Фото».
- Загрузка идёт по одному файлу; если конкретный файл не загрузился —
  остальные всё равно продолжают, в конце — точный список удачных/неудачных.
- При истечении access-токена мидбатча бот делает ровно одно обновление
  токена и повторяет только тот файл, что не загрузился — Google Drive не
  умеет "перезаписывать" файл по имени как Яндекс (`overwrite=true`), так что
  повтор всего пакета создал бы дубликаты; поэтому логика per-item.
- Удаление исходных сообщений из чата — best effort: если Telegram не даст
  удалить (например, сообщение слишком старое), бот сообщит об этом отдельно.
- Приложение в статусе **In Production** с несенситивным scope `drive.file`
  — по нашим данным это снимает лимит в 100 test-пользователей и должно
  убрать протухание refresh-токена через 7 дней (актуально для
  неверифицированных Testing-приложений). Стоит подтвердить эмпирически
  через неделю использования.
- Scope `drive.file`: бот видит только файлы/папки, которые сам создал —
  не весь Google Drive пользователя.
