# 🤖 Настройка модели DistilBERT

## ⚠️ Важно!
Модель DistilBERT (520MB) слишком большая для GitHub и не включена в репозиторий.

## 📥 Скачивание модели

### Вариант 1: Автоматическое скачивание
```bash
# Создайте папку models/ и скачайте модель
mkdir -p models/
cd models/

# Скачайте модель с Hugging Face
wget https://huggingface.co/your-model-name/resolve/main/model.safetensors
wget https://huggingface.co/your-model-name/resolve/main/config.json
wget https://huggingface.co/your-model-name/resolve/main/tokenizer.json
wget https://huggingface.co/your-model-name/resolve/main/tokenizer_config.json
wget https://huggingface.co/your-model-name/resolve/main/special_tokens_map.json
```

### Вариант 2: Через Python
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Скачать модель автоматически
model_name = "your-model-name"  # замените на имя вашей модели
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Сохранить локально
model.save_pretrained("./models/")
tokenizer.save_pretrained("./models/")
```

## 🔧 Альтернативные варианты хранения

1. **Google Drive** - загрузите модель в Google Drive и поделитесь ссылкой
2. **Hugging Face Hub** - загрузите модель на Hugging Face
3. **Dropbox/OneDrive** - используйте облачное хранилище
4. **Git LFS** - если у вас есть доступ к Git LFS

## 📝 Структура папки models/
```
models/
├── config.json
├── model.safetensors      # Основная модель (520MB)
├── tokenizer.json
├── tokenizer_config.json
├── special_tokens_map.json
└── training_args.bin
```

После скачивания модели бот будет работать корректно!
