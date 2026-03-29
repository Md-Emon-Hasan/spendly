from app import app
from database.connection import get_db

with app.test_request_context():
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = 2

        resp2 = c.get('/analytics')
        html2 = resp2.data.decode('utf-8')
        if 'Monthly Budget Usage' in html2:
            print("Found Monthly Budget Usage in Analytics")
            lines = html2.split('\n')
            for i, line in enumerate(lines):
                if 'Overall Monthly Budget (' in line:
                    print(lines[i].strip())
                    print(lines[i+1].strip())
                    print(lines[i+2].strip())
                    print(lines[i+3].strip())
                    print(lines[i+4].strip())
        else:
            print("NOT Found in Analytics")
            
        resp3 = c.get('/goals')
        html3 = resp3.data.decode('utf-8')
        if 'Monthly Budget Usage' in html3:
            print("Found Monthly Budget Usage in Goals")
            lines = html3.split('\n')
            for i, line in enumerate(lines):
                if 'Overall Monthly Budget<' in line or 'Overall Monthly Budget' in line:
                    print(lines[i].strip())
                    print(lines[i+1].strip())
                    print(lines[i+2].strip())
                    print(lines[i+3].strip())
                    print(lines[i+4].strip())
        else:
            print("NOT Found in Goals")
