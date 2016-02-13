from account_manager import AccountManager
from session_factory import SessionFactory
from followees_crawler import FolloweesCrawler

def main():
    account = AccountManager.get_account()
    session_factory = SessionFactory(account)
    session = session_factory.get_login_session()

    fc = FolloweesCrawler(session, 'jixin')
    fc.get_followees_page()

if __name__ == '__main__':
    main()