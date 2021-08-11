import os
import subprocess
import sys
import tkinter as tk
import requests
import api_handler as api
import db_handler as db
from tkinter import ttk
from datetime import datetime
from functools import partial
from PIL import Image, ImageTk
from win32api import GetSystemMetrics
from validator import error_window, validate_email, validate_password
from api_handler import countries, categories, languages

# globals
settings = {
    'country': countries[countries.index('ie')],
    'category': categories[categories.index('general')],
    'language': languages[languages.index('en')]
}
country_display = None
category_display = None
language_display = None
country_box_widget = None
category_box_widget = None
language_box_widget = None
search_entry = None
username_log_in = None
password_log_in = None
account_creation_variables = {}
articles = api.get_news(settings['country'], settings['category'], settings['language'])
if articles is None:
    sys.exit()
current_page = 0
articles_per_page = 6
account = None
# get width and height of screen
width = GetSystemMetrics(0)
height = GetSystemMetrics(1)

# root settings
root = tk.Tk()
root.title('Newsfeed')
root.geometry(str(width)+'x'+str(height))
root.configure(bg='white')
root.attributes("-fullscreen", True)
root.wm_attributes('-transparentcolor', 'green')

# top frame
top_frame = tk.Frame(root, bg='white')
top_frame.pack()

# news frame
centre_frame = tk.Frame(root)
centre_frame.pack()
centre_frame.configure(bg='white')

# returns articles from API based on current settings
def get_selected_news(keyword=''):
    global settings
    return api.get_news(settings['country'], settings['category'], settings['language'], keyword)

# refreshes top frame
def set_top_frame():
    global root, top_frame, country_display, category_display, language_display, search_entry

    # destroy all children from top_frame
    for child in top_frame.winfo_children():
        child.destroy()

    root.bind('<Return>', lambda event: search())

    # label with current time
    time_label = tk.Label(top_frame, text=datetime.now().strftime('%d/%m/%Y\n%H:%M:%S'), font=('Century', 12), bg='white', fg='navy')
    time_label.pack(side=tk.LEFT, padx=50)

    # displays create account/log in buttons if not logged in
    if account is None:
        create_account_button = tk.Button(top_frame, cursor='hand2', text='CREATE\nACCOUNT', font=('Century', 12), bg='#112288', fg='white', command=create_account_window)
        create_account_button.pack(side=tk.RIGHT, padx=50)
        login = tk.Button(top_frame, cursor='hand2', text='LOG IN', font=('Century', 12), bg='#112288', fg='white', command=log_in_window)
        login.pack(side=tk.RIGHT, padx=50)
    # displays welcome message, change current page button and log out button
    else:
        name = tk.Label(top_frame, text='Welcome to the News Room,\r\n' + account.get_name(), font=('Century', 12), bg='white')
        name.pack(side=tk.LEFT, padx=50)
        if account.get_current_state() == 'home':
            faves = tk.Button(top_frame, cursor='hand2', text='MY FAVOURITE\r\nARTICLES', font=('Century', 10), bg='#112288', fg='white', command=show_favourite_articles)
            faves.pack(side=tk.LEFT, padx=50)
        if account.get_current_state() == 'favourites':
            return_buttons = tk.Button(top_frame, cursor='hand2', text='RETURN TO\r\nHOME', font=('Century', 10), bg='#112288', fg='white', command=return_to_main)
            return_buttons.pack(side=tk.LEFT, padx=50)
        logout = tk.Button(top_frame, cursor='hand2', text='LOG OUT', bg='#112288', fg='white', command=log_out)
        logout.pack(side=tk.RIGHT, padx=50)

    # settings button
    tk.Button(top_frame, text='SETTINGS', cursor='hand2', font=('Century', 12), bg='#112288', fg='white', command=open_settings).pack(side=tk.LEFT, padx=50)

    # search entry
    tk.Button(top_frame, text='SEARCH', cursor='hand2', font=('Century', 12), bg='#112288', fg='white', command=search).pack(side=tk.RIGHT, padx=5)

    search_entry = tk.StringVar()
    tk.Entry(top_frame, textvariable=search_entry, font=('Century', 12), bg='white', fg='#000').pack(side=tk.RIGHT, padx=10)

    # displays currently displayed articles settings
    if account is None or account.get_current_state() == 'home':
        category_display = tk.Label(top_frame, text='Category: ' + settings['category'].upper(), font=('Century', 12), bg='white')
        category_display.pack(side=tk.BOTTOM)

        country_display = tk.Label(top_frame, text='Country: ' + settings['country'].upper(), font=('Century', 12), bg='white')
        country_display.pack(side=tk.BOTTOM)

        language_display = tk.Label(top_frame, text='Language: ' + settings['language'].upper(), font=('Century', 12), bg='white')
        language_display.pack(side=tk.BOTTOM)

    # updates the time every second
    def update_time():
        current_time = datetime.now()
        time_label.configure(text=current_time.strftime('%d/%m/%Y\n%H:%M:%S'), font=('Century', 12))
        time_label.after(1000, update_time)

    time_label.after(1000, update_time)

# display list of articles
def display_articles():
    global centre_frame, account, country_display, category_display, language_display, settings, articles

    # update current settings
    if account is None or account.get_current_state() == 'home':
        country_display.configure(text='Country: ' + settings['country'].upper())
        category_display.configure(text='Category: ' + settings['category'].upper())
        language_display.configure(text='Language: ' + settings['language'].upper())
    row = 0
    column = 0

    # articles loop
    for i, article in enumerate(articles[current_page * articles_per_page:(current_page * articles_per_page) + articles_per_page]):
        # create new frame for each article
        article_frame = tk.Frame(centre_frame)
        article_frame.configure(bg='white', highlightbackground='black', highlightthickness=2, width=int(width / 3.1), height=int(height / 3))

        # show image
        photo_img = get_image(article['urlToImage'], int(width / 8), int(width / 25))
        img = tk.Label(article_frame, image=photo_img)
        img.img = photo_img
        img.grid(row=0, column=0)

        # title
        title = tk.Label(article_frame, text=article['title'], font=('Century', 12), bg='white', fg='#000', wraplength=int((width / 3.15)))
        title.grid(row=1, column=0)

        # source
        source = tk.Label(article_frame, text=article['source']['name']+': ', font=('Century', 8), bg='white', fg='gray')
        source.grid(row=2, column=0, sticky='w')

        # author
        author = tk.Label(article_frame, text=article['author'], font=('Century', 8), bg='white', fg='gray')
        author.grid(row=2, column=0)

        # description
        description = tk.Label(article_frame, text=article['description'], font=('Century', 12), fg='#444', bg='white', wraplength=int(width / 3.15))
        description.grid(row=3, column=0)

        # more information button
        more = tk.Button(article_frame, text='View more', font=('Century', 10), cursor='hand2', bg='#bbc0c4', command=partial(open_more, article))
        more.grid(row=4, column=0, pady=5)

        # if user is logged in, show stars
        if account is not None:
            if str(article) in account.get_favourites(): img = Image.open('./filled_star.png')
            else: img = Image.open('./hollow_star.png')
            photo_image_star = ImageTk.PhotoImage(img)
            save = tk.Button(article_frame, image=photo_image_star, bg='white', cursor='hand2', command=partial(favourite_article, article), highlightthickness=0, bd=0)
            save.img = photo_image_star
            save
            save.grid(row=4, column=0, sticky='e')

        # frame size within grid adjustment
        article_frame.grid(sticky='nswe', row=row, column=column, padx=5, pady=3)
        article_frame.rowconfigure(0, weight=1)
        article_frame.columnconfigure(0, weight=1)
        article_frame.grid_propagate(0)

        # centralise all children in the frame
        for child in article_frame.winfo_children():
            child.configure(justify=tk.CENTER)

        # adjust article position
        column += 1
        if column > 2:
            column = 0
            row += 1

    # if no articles were found, display message
    if len(articles) == 0:
        error_message = tk.StringVar()
        error_message.set('No articles found.\r\nPlease try changing country or language in your settings.\r\nOr try a different term for the search.')
        tk.Label(centre_frame, textvariable=error_message, bg='white', fg='red').grid(row=0, column=0)
        if account is not None:
            if account.get_current_state() == 'favourites':
                error_message.set('You haven\'t saved any articles to your favourites yet!')
    else:
        # adjusts number of existing pages
        total_pages = int(len(articles) / articles_per_page)
        if len(articles) % articles_per_page != 0: total_pages += 1
        if total_pages == 0: total_pages = 1

        # page label
        pages_label = tk.Label(centre_frame, text='PAGE', font=('Century', 14), bg='white', fg='#000')
        pages_label.configure(justify=tk.CENTER)
        pages_label.grid(row=5, column=0, columnspan=total_pages)

        # pages buttons frame
        total_frame = tk.Frame(centre_frame)
        total_frame.configure(bg='white')
        total_frame.grid(row=6, column=0, columnspan=4)

        # for loop to create buttons for each available page of articles
        for i in range(total_pages):
            total_frame.rowconfigure(i, weight=1)
            num = tk.Button(total_frame, text=str(i + 1), cursor='hand2', font=('Century', 12), bg='white', fg='#000', command=partial(change_page, i))
            if i == current_page: num.configure(bg='#112288', fg='white')
            num.grid(row=6, column=i, padx=5)

# settings window pop up
def open_settings():
    global country_box_widget, language_box_widget, category_box_widget
    # creates new window
    settings_window_root = tk.Tk()
    settings_window_root.resizable(0, 0)
    settings_window_root.configure(bg='grey', highlightbackground='black', highlightthickness=5)
    settings_window_root.title('Settings')
    settings_window_root.geometry('230x160')
    settings_window_root.overrideredirect(1)
    settings_window_root.eval('tk::PlaceWindow . center')
    settings_window_root.focus_force()
    settings_window_root.bind('<Return>', lambda event: select_settings(settings_window_root))

    settings_title_label = tk.Label(settings_window_root, text='Settings:', bg='grey', fg='white')
    settings_title_label.grid(column=0, row=0, columnspan=2)

    # countries
    tk.Label(settings_window_root, text='Country:', bg='grey', fg='white').grid(row=1, column=0)
    country_stringvar = tk.StringVar()
    country_box_widget = ttk.Combobox(settings_window_root, textvariable=country_stringvar)
    country_box_widget['values'] = countries
    country_box_widget.grid(row=1, column=1, pady=5)
    country_box_widget.current(countries.index(settings['country']))

    # languages
    tk.Label(settings_window_root, text='Language: ', bg='grey', fg='white').grid(row=2, column=0)
    language_stringvar = tk.StringVar()
    language_box_widget = ttk.Combobox(settings_window_root, textvariable=language_stringvar)
    language_box_widget['values'] = languages
    language_box_widget.grid(row=2, column=1, pady=5)
    language_box_widget.current(languages.index(settings['language']))

    # categories
    tk.Label(settings_window_root, text='Category: ', bg='grey', fg='white').grid(row=3, column=0)
    category_stringvar = tk.StringVar()
    category_box_widget = ttk.Combobox(settings_window_root, textvariable=category_stringvar)
    category_box_widget['values'] = categories
    category_box_widget.grid(row=3, column=1, pady=5)
    category_box_widget.current(categories.index(settings['category']))

    # buttons
    cancel = tk.Button(settings_window_root, text='CANCEL', cursor='hand2', command=settings_window_root.destroy)
    cancel.grid(row=4, column=0, pady=10)

    confirm = tk.Button(settings_window_root, text='APPLY', cursor='hand2', command=partial(select_settings, settings_window_root))
    confirm.grid(row=4, column=1, pady=10)

    settings_window_root.grid()

    country_box_widget.focus_set()

    settings_window_root.mainloop()

# updates settings and goes to home screen
def select_settings(r):
    global settings, country_box_widget, category_box_widget, current_page, articles

    # updates settings
    settings['country'] = country_box_widget.get()
    settings['category'] = category_box_widget.get()
    settings['language'] = language_box_widget.get()

    # updates account's settings on both the database and the local object
    if account is not None:
        account.update_settings(settings)
        db.update_settings(account, settings)

    # updates screen and destroys settings window
    r.destroy()
    current_page = 0
    if account is not None:
        account.set_current_state('home')
    articles = get_selected_news()
    update_screen()

# create account window pop up
def create_account_window():
    global account_creation_variables

    # creates window
    create_account_root = tk.Tk()
    create_account_root.resizable(0, 0)
    create_account_root.configure(bg='grey', highlightbackground='black', highlightthickness=5)
    create_account_root.title('Create account')
    create_account_root.geometry('400x330')
    create_account_root.overrideredirect(1)
    create_account_root.eval('tk::PlaceWindow . center')
    create_account_root.focus_force()
    create_account_root.bind('<Return>', lambda event: create_account(create_account_root))

    tk.Label(create_account_root, text='New Account', bg='grey', fg='white', font=('Century', 14), anchor=tk.CENTER).grid(row=0, column=0, columnspan=2)

    # name label + entry
    tk.Label(create_account_root, text='Name', bg='grey', fg='white').grid(row=1, column=0, padx=5)
    account_creation_variables['name'] = tk.StringVar(create_account_root)
    name_entry = tk.Entry(create_account_root, textvariable=account_creation_variables['name'])
    name_entry.grid(row=2, column=0, pady=5, padx=5)

    # surname
    tk.Label(create_account_root, text='Surname', bg='grey', fg='white').grid(row=1, column=1)
    account_creation_variables['surname'] = tk.StringVar(create_account_root)
    surname_entry = tk.Entry(create_account_root, textvariable=account_creation_variables['surname'])
    surname_entry.grid(row=2, column=1, pady=5, padx=5)

    # email
    tk.Label(create_account_root, text='Email', bg='grey', fg='white').grid(row=3, column=0, columnspan=2)
    account_creation_variables['email'] = tk.StringVar(create_account_root)
    email_entry = tk.Entry(create_account_root, textvariable=account_creation_variables['email'])
    email_entry.grid(row=4, column=0, pady=5, columnspan=2)

    # password
    tk.Label(create_account_root, text='Password', bg='grey', fg='white').grid(row=5, column=0, columnspan=2)
    account_creation_variables['password'] = tk.StringVar(create_account_root)
    password_entry = tk.Entry(create_account_root, show='\u2022', textvariable=account_creation_variables['password'])
    password_entry.grid(row=6, column=0, pady=5, columnspan=2)

    # confirm password
    tk.Label(create_account_root, text='Confirm password', bg='grey', fg='white').grid(row=7, column=0, columnspan=2)
    account_creation_variables['confirm'] = tk.StringVar(create_account_root)
    confirm_password_entry = tk.Entry(create_account_root, show='\u2022', textvariable=account_creation_variables['confirm'])
    confirm_password_entry.grid(row=8, column=0, pady=5, columnspan=2)

    # buttons
    tk.Button(create_account_root, text='CANCEL', cursor='hand2', command=lambda: create_account_root.destroy()).grid(row=9, column=0, pady=10, padx=10)
    tk.Button(create_account_root, text='CREATE', cursor='hand2', command=partial(create_account, create_account_root)).grid(row=9, column=1, pady=10)

    # standardises font
    for child in create_account_root.winfo_children():
        if child.cget('font') == 'TkDefaultFont' or child.cget('font') == 'TkTextFont':
            child.configure(font=('Century', 12))

    create_account_root.grid()

    name_entry.focus_set()

    create_account_root.mainloop()

# creates account based on create account window
def create_account(window):
    global account_creation_variables, settings

    # all fields must be at least 1 character long
    for var in account_creation_variables:
        if len(account_creation_variables[var].get()) <= 1:
            error_window('Empty fields', 'Please fill in all the blanks with at least two characters.')
            return

    # email must follow proper email format
    if not validate_email(account_creation_variables['email'].get()):
        error_window('Invalid email address', 'Please insert a valid email address.')
        return

    # password must match the confirmation password
    if account_creation_variables['password'].get() != account_creation_variables['confirm'].get():
        error_window('Passwords don\'t match', ' Please try again.')
        return

    # password must follow proper password format
    if not validate_password(account_creation_variables['password'].get()):
        error_window('Invalid password', 'Your password must contain at least:\n8 characters, one lower letter, one capital letter,\none number and one special character.')
        return

    # creates account on database and destroy create account window
    db.create_account(account_creation_variables['name'].get(), account_creation_variables['surname'].get(), account_creation_variables['email'].get(), account_creation_variables['password'].get(), settings['country'], settings['language'], settings['category'])
    window.destroy()

# creates log in window pop up
def log_in_window():
    global username_log_in, password_log_in

    # create window
    r = tk.Tk()
    r.resizable(0, 0)
    r.configure(bg='grey', highlightbackground='black', highlightthickness=5)
    r.title('Log In')
    r.geometry('250x120')
    r.overrideredirect(1)
    r.eval('tk::PlaceWindow . center')
    r.focus_force()
    r.bind('<Return>', lambda event: log_in(r))

    tk.Label(r, text='LOG IN', bg='grey', fg='white').grid(row=0, column=0, columnspan=2)

    # email
    tk.Label(r, text='EMAIL:', bg='grey', fg='white').grid(row=1, column=0)
    username_log_in = tk.StringVar(r)
    login = tk.Entry(r, textvariable=username_log_in)
    login.grid(row=1, column=1)

    # password
    tk.Label(r, text='PASSWORD', bg='grey', fg='white').grid(row=2, column=0)
    password_log_in = tk.StringVar(r)
    password = tk.Entry(r, show='\u2022', textvariable=password_log_in)
    password.grid(row=2, column=1)

    # buttons
    cancel = tk.Button(r, text='CANCEL', fg='#000', cursor='hand2', command=r.destroy)
    cancel.grid(row=3, column=0, pady=10)

    login_button = tk.Button(r, text='LOG IN', fg='#000', cursor='hand2', command=partial(log_in, r))
    login_button.grid(row=3, column=1, pady=10)

    # standardise font
    for child in r.winfo_children():
        child.configure(font=('Century', 10))

    r.grid()

    login.focus_set()

    r.mainloop()

# log in based on log in pop up
def log_in(window):
    global account, settings, username_log_in, password_log_in, articles, current_page

    # sets local variables
    username = username_log_in.get()
    password = password_log_in.get()

    # all fields must have at least 6 characters
    if len(username) < 5 or len(password) < 5:
        error_window('Empty fields', 'Please fill in all the blanks')
        return

    # email must follow proper email pattern
    if not validate_email(username):
        error_window('Invalid email address', 'Please insert a valid email address.')
        return

    # gets account from database
    account = db.get_account(username, password)

    # if get_account return None, there has been an error
    if account is None:
        error_window('Unable to log in', 'Please try again.')

    # updates Tk()
    window.destroy()
    if settings != account.get_settings():
        settings = account.get_settings()
    account.set_current_state('home')
    current_page = 0
    articles = get_selected_news()
    update_screen()

# sets account to None and returns user to home screen
def log_out():
    global current_page, account, articles

    if account.get_current_state() != 'home': current_page = 0
    account = None
    articles = get_selected_news()
    update_screen()

# displays user's favourite articles
def show_favourite_articles():
    global account, current_page, articles

    current_page = 0
    account.set_current_state('favourites')
    articles = account.get_json_favourites()
    update_screen()

# displays home screen
def return_to_main():
    global current_page, articles

    current_page = 0
    account.set_current_state('home')
    articles = get_selected_news()
    update_screen()

# opens a link on a web browser
def open_browser(url):
    if sys.platform == 'win32':
        os.startfile(url)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', url])
    else:
        try:
            subprocess.Popen(['xdg-open', url])
        except OSError:
            error_window('Please open a browser on: ', url)

# new window with further information about the news article
def open_more(article):
    # new window root
    read_more_root = tk.Toplevel()
    read_more_root.title(article['title'])
    read_more_root.geometry('800x600')
    read_more_root.configure(bg='white')
    read_more_root.resizable(0, 0)

    # image
    photo_img = get_image(article['urlToImage'], 400, 200)
    img = tk.Label(read_more_root, image=photo_img)
    img.img = photo_img
    img.pack()

    # title
    title = tk.Label(read_more_root, text=article['title'], font=('Century', 20), bg='#112288', fg='white', wraplength=700, padx=10, pady=5)
    title.pack(fill=tk.X)

    # author
    author = tk.Label(read_more_root, text=article['author'], font=('Century', 10), bg='white', fg='gray')
    author.pack()

    # source
    source = tk.Label(read_more_root, text='Source: ' + article['source']['name'], font=('Century', 10), bg='white')
    source.pack()

    # date and time article was published
    published = tk.Label(read_more_root, text='Published: ' + article['publishedAt'].replace('T', ' ').replace('Z', ' '), font=('Century', 10), bg='white')
    published.pack()

    # content
    content = tk.Label(read_more_root, text=article['content'][0:-14], font=('Century', 12), bg='white', wraplength=500, borderwidth=2, relief='groove', fg='#000', padx=10, pady=5)
    content.pack()

    # read online button
    online = tk.Button(read_more_root, text='Read online', font=('Century', 12), cursor='hand2', bg='white', fg='blue', command=partial(open_browser, article['url']), padx=10, pady=5)
    online.pack(pady=20)

    online.focus_set()

# updates current page
def change_page(num):
    global current_page

    current_page = num
    update_screen()

# adds or removes article from favourites both locally and on database
def favourite_article(article):
    global account, current_page, articles

    # remove article if already in favourites
    if str(article) in account.get_favourites():
        account.remove_favourite(str(article))
        db.remove_favourite(account, str(article))

        # changes current page if removing last favourite article from the last page
        if account.get_current_state() == 'favourites' and len(account.get_favourites()) % articles_per_page == 0:
            current_page -= 1
            if current_page == -1:
                current_page = 0
    # adds article if it isn't in the favourites
    else:
        account.add_favourite(str(article).replace('\n', '\\n').replace('\r\n', '\\r\\n'))
        db.add_favourite(account, str(article).replace('\n', '\\n').replace('\r\n', '\\r\\n'))

    if account.get_current_state() == 'favourites':
        articles = account.get_json_favourites()

    update_screen()

# returns image from http url
def get_image(url, w, h):
    try:
        img = Image.open(requests.get(url, stream=True).raw).resize((w, h), Image.ANTIALIAS)
    except:
        # if any errors occur, a placeholder is created
        img = Image.open('./no_image.png')
    return ImageTk.PhotoImage(img)

# updates Tk()
def update_screen():
    global root, articles, account

    set_top_frame()
    for child in centre_frame.winfo_children():
        child.destroy()
    display_articles()

def search():
    global search_entry, articles

    if len(search_entry.get()) < 1:
        error_window('Search', 'Please enter something to search for.')
        return

    articles = get_selected_news(keyword=search_entry.get())
    update_screen()

# calls function to display list of articles
update_screen()

root.mainloop()
