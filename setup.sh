mkdir -p ~/.streamlit/
echo "\
[server]\n\
port = 8501\n\
headless = true\n\
enableCORS = true\n\
enableXsrfProtection = false\n\
" > ~/.streamlit/config.toml