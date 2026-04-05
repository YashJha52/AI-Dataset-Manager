import os
import glob
import re

directory = r"c:\Users\mhatr\OneDrive\Desktop\programming files\DBMS\AI-Dataset-Manager\frontend"
html_files = glob.glob(os.path.join(directory, "*.html"))

premium_css = """    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --surface-color: #1e293b;
            --primary-color: #6366f1;
            --primary-hover: #818cf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: rgba(255, 255, 255, 0.1);
            --glass-bg: rgba(30, 41, 59, 0.6);
        }

        body {
            background: radial-gradient(circle at top right, #1e1b4b, #0f172a 40%, #020617);
            background-attachment: fixed;
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
        }

        /* Glassmorphism Navbar */
        .navbar {
            background: rgba(15, 23, 42, 0.5) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            padding: 1.25rem 0;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }
        
        .navbar-brand {
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #a5b4fc, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Premium Glass Card */
        .card {
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            color: var(--text-main);
        }

        .card:hover {
            transform: translateY(-4px) scale(1.01);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
            background: rgba(30, 41, 59, 0.75);
        }

        .card-header {
            background: rgba(255, 255, 255, 0.03) !important;
            border-bottom: 1px solid var(--border-color);
            font-weight: 600;
            color: var(--text-main) !important;
            padding: 1.25rem 1.5rem;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-size: 0.85rem;
        }
        
        .card-body {
            padding: 2rem;
        }

        .card-title {
            font-weight: 600;
            letter-spacing: -0.025em;
            margin-bottom: 1rem;
        }

        /* Forms & Inputs */
        .form-control {
            background-color: rgba(15, 23, 42, 0.5);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            transition: all 0.2s;
        }

        .form-control:focus {
            background-color: rgba(15, 23, 42, 0.8);
            border-color: var(--primary-color);
            color: var(--text-main);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
            outline: none;
        }

        .form-control::placeholder {
            color: rgba(148, 163, 184, 0.6);
        }

        /* Buttons Update */
        .btn {
            border-radius: 10px;
            font-weight: 500;
            padding: 0.6rem 1.2rem;
            transition: all 0.3s ease;
            letter-spacing: 0.025em;
            text-transform: none;
        }

        .btn-primary, .btn-info, .btn-success, .btn-warning {
            background: linear-gradient(135deg, var(--primary-color) 0%, #4f46e5 100%);
            border: none;
            color: white !important;
            box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
        }

        .btn-primary:hover, .btn-info:hover, .btn-success:hover, .btn-warning:hover {
            background: linear-gradient(135deg, var(--primary-hover) 0%, var(--primary-color) 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 15px -2px rgba(99, 102, 241, 0.5);
            color: white !important;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
            border: none;
        }
        .btn-danger:hover {
             transform: translateY(-2px);
             box-shadow: 0 6px 15px -2px rgba(239, 68, 68, 0.5);
        }

        .btn-outline-light {
            border-color: rgba(255,255,255,0.2);
            color: var(--text-main);
        }
        
        .btn-outline-light:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,0.3);
            color: #fff;
        }

        .btn-outline-primary, .btn-outline-success, .btn-outline-secondary {
            border-color: rgba(255,255,255,0.2);
            color: var(--text-main);
        }
        .btn-outline-primary:hover, .btn-outline-success:hover, .btn-outline-secondary:hover {
            background: rgba(255,255,255,0.1);
            color: #fff;
        }

        /* Generic Background color overrides */
        .bg-primary, .bg-secondary, .bg-success, .bg-warning, .bg-info, .bg-dark {
            background: rgba(255, 255, 255, 0.03) !important;
        }
        
        .fw-bold { font-weight: 600 !important; }
        .text-dark { color: var(--text-main) !important; }
        .text-muted { color: var(--text-muted) !important; }

        .list-group-item {
            background: transparent;
            border-color: var(--border-color);
            color: var(--text-main);
            padding: 1.25rem 1.5rem;
            transition: background 0.2s;
        }
        
        .list-group-item:hover {
            background: rgba(255, 255, 255, 0.02);
        }
        
        /* Badges */
        .badge {
            font-weight: 500;
            padding: 0.4em 0.8em;
            border-radius: 6px;
            border-color: rgba(255,255,255,0.1);
        }
        .badge.bg-light {
            background-color: rgba(255,255,255,0.1) !important;
            color: var(--text-main) !important;
            border-color: transparent !important;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .card { animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; }
        .col-md-4:nth-child(1) .card { animation-delay: 0.05s; }
        .col-md-4:nth-child(2) .card { animation-delay: 0.15s; }
        .col-md-4:nth-child(3) .card { animation-delay: 0.25s; }
        .col-md-4:nth-child(4) .card { animation-delay: 0.35s; }
        .col-md-5 .card { animation-delay: 0.1s; }
        .col-md-7 .card { animation-delay: 0.2s; }

    </style>
</head>
<body>
"""

for path in html_files:
    # Skip dashboard.html because we will overwrite it completely to fix its layout issues
    if "dashboard.html" in path:
        continue

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the base Bootstrap CSS link and the opening body tag
    content = re.sub(r'<link.*?bootstrap\.min\.css.*?>(\s*)</head>(\s*)<body[^>]*>', premium_css, content, count=1, flags=re.IGNORECASE|re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Updated: {path}")

print("Done updating HTML files.")
