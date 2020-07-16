from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk         # for tab management 
from PIL import ImageTk, Image
import sqlite3
import os
import sys
import io # this library is needed to make the binary image data readable for the PIL modules
from selenium import webdriver 
from pygame import mixer


class Login:
    # empty labels are made to manage spacings
    def __init__(self, master):
        my_frame = Frame(master)
        my_frame.pack()
        
        # defining the labels and entries(input boxes)
        global username_entry
        global password_entry
        username_label = Label(my_frame, text='Username: ', font='Helvetica 11')
        username_entry = Entry(my_frame, font='Times 14')
        
        password_label = Label(my_frame, text='Password: ', font='Helvetica 11')
        password_entry = Entry(my_frame, show='*', font='Times 14')

        # defining blank labels
        blank = Label(my_frame, text='')

        # defining buttons
        login_button = Button(my_frame, text='Login', font='12', command=self.checkAccount)
        cancel_button = Button(my_frame, text='Cancel', font='12', command=lambda: self.getOut(master))


        # putting these on the screen

        username_label.grid(row=0, column=0, pady=40)
        username_entry.grid(row=0, column=1, pady=40)
        password_label.grid(row=1, column=0)
        password_entry.grid(row=1, column=1)

        blank.grid(row=2, column=0, columnspan=2, pady=30)

        login_button.grid(row=3, column=0, columnspan=2,ipadx=70, pady=10, ipady=7)
        cancel_button.grid(row=4, column=0, columnspan=2, ipadx=68, pady=10, ipady=7)

        # putting another empty label
        blank_2 = Label(my_frame, text=' ')
        blank_2.grid(row=5, column=0, columnspan=2, pady=40)

        # putting a label and a button to route it for registration
        sign_up_label = Label(my_frame, text="Don't have an account?")
        sign_up_button = Button(my_frame, text='Sign Up', command=lambda: self.Reg(master))

        sign_up_label.grid(row=6, column=0)
        sign_up_button.grid(row=6, column=1)

    def getOut(self, master): # taking root/master as the argument
        master.destroy()
    
    def Reg(self, master):
        master.destroy()
        signUp()

    def checkAccount(self): # will check if the user exists
        x = username_entry.get() # will send 'x' as argument in accountWindow()

        # connecing to the database 
        con = sqlite3.connect('accounts_3.db')
        
        # creating a cursor
        currsor = con.cursor()
        
        # now executing the query
        currsor.execute("SELECT * FROM accounts WHERE username = ? AND password = ?",(username_entry.get(), password_entry.get()))
        if currsor.fetchone() == None:
            messagebox.showerror('Wrong Credentials', 'Incorrect Username or Password')
            username_entry.delete(0, END)
            password_entry.delete(0, END)
        else:
            accountWindow(x) # sending the username as the argument in order to open user's window
            
        con.commit()
        con.close()


class PersonalAccount:
    def __init__(self, master, use_name):
        # creating a notebook to manage tabs
        my_notebook = ttk.Notebook(master)
        my_notebook.pack(pady=5)

        #frame1 = Frame(my_notebook, width=1100, height=1000)
        frame2 = Frame(my_notebook, width=1100, height=1000)
        frame3 = Frame(my_notebook, width=1100, height=1000)
        frame4 = Frame(my_notebook, width=1100, height=1000)

        frame2.pack(fill='both', expand=1)
        frame3.pack(fill='both', expand=1)
        frame4.pack(fill='both', expand=1)

        
        my_notebook.add(frame2, text='Local')
        my_notebook.add(frame3, text='Favourites')
        my_notebook.add(frame4, text='Profile')


        # retriving all the user data

        connection = sqlite3.connect('accounts_3.db')
        curse = connection.cursor()

        curse.execute("""SELECT * FROM accounts WHERE username=?""", (use_name,))
        account_details = curse.fetchone() 
        # the trick to avoid TypeError: 
        # completely store the fetchone() tuple in a varible
        # then commit and close the connection
        # then use the tuple saved in that variable to get the details

        connection.commit()
        connection.close()
        f_name = account_details[0]
        l_name = account_details[1]
        Password = account_details[4]


        # Working on Profile

        # opening a another data to see if the user
        # has an DP saved
        # if there is no dp, a blank picture will be saved as dp

        connection_2 = sqlite3.connect('intra_account.db')
        c_2 = connection_2.cursor()
        
        c_2.execute("""SELECT * FROM userdata WHERE username=?""",(use_name,))
        
        dp_data = c_2.fetchone()
        connection_2.commit()


        if dp_data==None:
            conn_ = sqlite3.connect('blankdp.db')
            c_ = conn_.cursor()
            c_.execute("SELECT * FROM blank")
            dp_ = c_.fetchone()
            conn_.commit()
            conn_.close() 
            
            img = io.BytesIO(dp_[0])
            my_img = Image.open(img).resize((250, 250), Image.ANTIALIAS)
            ph = ImageTk.PhotoImage(my_img)
            img_label = Label(frame4, image=ph)
            img_label.image = ph
            img_label.grid(row=0, column=0)
            
        else:
            my_img = dp_data[1] #my_img is in binary
            my_img = io.BytesIO(my_img)
            image = Image.open(my_img).resize((250, 250), Image.ANTIALIAS)
            ph = ImageTk.PhotoImage(image)
            label_1 = Label(frame4, image=ph)
            label_1.image = ph
            label_1.grid(row=0, column=0)
        
        connection_2.commit()
        connection_2.close()
        
        

        # Working on Frame 4
        name_label = Label(frame4, text=f_name + ' ' + l_name)
        name_label.grid(row=1, column=0)
        
        # Button to change DP
        change_dp_button = Button(frame4, text='Change Picture', command=lambda: self.changeDP(use_name, frame4))
        change_dp_button.grid(row=0, column=1, pady=1)

        # Adding a drop down menu, to change profile information
        def selectChange(event):
            if clicker.get()=='Change Name':
                changeName(use_name, frame4)
            
            elif clicker.get()=='Change Username':
                Phase(f_name, l_name, use_name, Password)
            
            elif clicker.get()=='Change Official Information':
                changeOfficialInfo(use_name)
        clicker = StringVar()
        clicker.set('Update')
        options = ['Change Name', 'Change Username', 'Change Official Information']
        option_menu = OptionMenu(frame4, clicker, *options, command=selectChange)
        option_menu.grid(row=0, column=2)
        

        # Working with Frame 2
        path = 'E:\Audio'
        lis = os.listdir(path)
        
        # Adding local music

        my_listbox = Listbox(frame2, width=170, height=14, bg='white', fg='black')
        my_listbox.pack(pady=2)

        for i in lis:
            my_listbox.insert(END, i)

        # creating a frame, here will be the buttons
        my_frame = Frame(frame2)
        my_frame.pack()

        stop_button = Button(my_frame, text='Stop')
        play_button = Button(my_frame, text='Play', command=lambda: self.playSong(my_listbox))
        pause_button = Button(my_frame, text='Pause')
        unpause_button = Button(my_frame, text='Unpause')
        
        # Adding a favourite button
        favourite_button = Button(my_frame, text='Add to Favourites', command= lambda: self.addFavourite(use_name, my_listbox, my_listbox_2))

        # this button will open the browser and the user can browse a vast amount of songs online
        website_button = Button(my_frame, text='Browse More Online', command=self.browseOnline)

        stop_button.grid(row=0, column=0, padx = 10)
        play_button.grid(row=0, column=1, padx = 10)
        pause_button.grid(row=0, column=2, padx = 10)
        unpause_button.grid(row=0, column=3, padx=10)
        website_button.grid(row=1, column=0, columnspan=4, ipadx=100)
        favourite_button.grid(row=2, column=0, columnspan=4, ipadx=110)


        # Working on Frame 3
        # creating a listbox

        my_listbox_2 = Listbox(frame3, width=175, height=37, bg='white', fg='black')
        my_listbox_2.pack()

        # If the user has the favourite songs saved in the Favourite.db database
        # it will show up
        # otherwise the listbox will be empty
        
        # now checking the database
        connection_4 = sqlite3.connect('Favourite.db')
        cu = connection_4.cursor()
        cu.execute('SELECT * FROM usersongs WHERE username=?', (use_name,))
        fav_songs_list = cu.fetchall()
        connection_4.commit()
        connection_4.close()
        
        # checking if the list is empty of not
        # if it is empty all of the songs will be added to the listbox
        if len(fav_songs_list)>0:
            for songs in fav_songs_list:
                my_listbox_2.insert(END, songs[1])

    def playSong(self, my_listbox):
        def pause():
            mixer.music.pause()
        x = my_listbox.get(ANCHOR)
        muse = Toplevel()
        muse.geometry('300x200')
        muse.title('Playing Song')
        mixer.init()
        pause_button = Button(muse, text='Pause', command=pause)
        pause_button.pack()
        mixer.music.load('E:/Audio/'+x)
        mixer.music.set_volume(0.7)
        mixer.music.play()
    
        # FAVOURITE MECHANISM IS NOT COMPLETE!(UPDATE: IT IS COMPLETE)
    def addFavourite(self, use_name, my_listbox, my_listbox_2):
        # Save the song long with the username in the database
        num = 0
        connect = sqlite3.connect('Favourite.db')
        curs = connect.cursor()
        curs.execute("SELECT * FROM usersongs WHERE username=?", (use_name,))
        check_fav = curs.fetchall()
        connect.commit()
        

        for i in check_fav:
            if i[1] == my_listbox.get(ANCHOR):
                num = 1
        
        if num == 0:

        
            curs.execute("INSERT INTO usersongs VALUES (?, ?)",(use_name, my_listbox.get(ANCHOR)))


            connect.commit()

            curs.execute("SELECT * FROM usersongs WHERE username=?", (use_name,))
            d = curs.fetchall()

            connect.close()
            songs= d[-1]
            my_listbox_2.insert(END, songs[1])
        
        else:
            messagebox.showinfo('Favourites', 'The song has been already to your favourites.')


    def changeDP(self, use_name, frame4):
        # dp -> name for the variable containing the profile picture image
        dp = filedialog.askopenfilename(initialdir='D:/Python', title='Select a picture', filetype=(('JPEG files', '*.jpg'), ('All files', '*.*')))
        print(dp)
        # reading the dp in binary
        with open(dp, 'rb') as fptr:
            dp_img = fptr.read()
        
        # check if dp already exists in database
        connection_3 = sqlite3.connect('intra_account.db')
        c_3 = connection_3.cursor()
        c_3.execute('SELECT * FROM userdata WHERE username=?',(use_name,))
        f_file = c_3.fetchone()
        connection_3.commit()
        
        # if None is found
        # it means the user never uploaded a profile picture
        # so, it will insert 

        if f_file == None:
            print('ok')
            c_3.execute('INSERT INTO userdata VALUES (?, ?)', (use_name, dp_img))
            connection_3.commit()


        else:
            c_3.execute("""UPDATE userdata SET dp=:dp
            WHERE username=:username""",
            {'username': use_name, 'dp': dp_img})
            connection_3.commit()
        
        c_3.execute("SELECT * FROM userdata WHERE username=?",(use_name,))
        x = c_3.fetchone()[1]
        connection_3.commit()

        img = io.BytesIO(x)
        ima_ge = Image.open(img).resize((250, 250), Image.ANTIALIAS)
        ph = ImageTk.PhotoImage(ima_ge)
        lab = Label(frame4, image=ph)
        lab.image = ph
        lab.grid(row=0, column=0)
        
        #messagebox.showinfo('Profile Photo', 'Restart the window to see changes.')
        connection_3.close()
        
    
    # function to open the browser and loading a website where you can broswe/listen to music 
    def browseOnline(self):
        driver = webdriver.Chrome(executable_path='C:/bin/chromedriver.exe')
        driver.get('https://www.jamendo.com/community/all-genres/tracks')       
        
    




    # class for registration
class Registration:

    def __init__(self, slave):
        second_frame = Frame(slave)
        second_frame.pack()

        # adding a few blank labels

        blenk_label = Label(second_frame)
        blenk_label.grid(row=0, column=0, columnspan=2)

        # details entries and their corresponding buttons
        first_name_label = Label(second_frame, text='First Name: ', font='11')
        last_name_label = Label(second_frame, text='Last Name: ', font='11')
        email_label = Label(second_frame, text='Email: ', font='11')
        user_name_label = Label(second_frame, text='Username: ', font='11')
        pass_word_label = Label(second_frame, text='Password', font='11')

        global first_name_entry
        global last_name_entry
        global email_entry
        global user_name_entry
        global pass_word_entry
        first_name_entry = Entry(second_frame, width=22, font='11')
        last_name_entry = Entry(second_frame, width=22, font='11')
        email_entry = Entry(second_frame, width=22, font='11')
        user_name_entry = Entry(second_frame, width=22, font='11')
        pass_word_entry = Entry(second_frame, show='*', width=22, font='11')


        first_name_label.grid(row=1, column=0, pady=10, ipadx=10)
        last_name_label.grid(row=2, column=0, pady=5)
        email_label.grid(row=3, column=0, pady=5)
        user_name_label.grid(row=4, column=0, pady=5)
        pass_word_label.grid(row=5, column=0, pady=5)

        first_name_entry.grid(row=1, column=1, pady=10)
        last_name_entry.grid(row=2, column=1, pady=5)
        email_entry.grid(row=3, column=1, pady=5)
        user_name_entry.grid(row=4, column=1, pady=5)
        pass_word_entry.grid(row=5, column=1, pady=5)

        # adding another blank label
        blenk_label_2 = Label(second_frame, text='')
        blenk_label_2.grid(row=6, column=0, columnspan=2, pady=10)

        #sign up button
        reg_button = Button(second_frame, text='Sign Up', command=self.addData)
        reg_button.grid(row=7, column=0, columnspan=2, ipadx=100)

    def addData(self):
        # checking if the entry spaces are blank

        if str(first_name_entry.get().isspace()) == True or first_name_entry.get()=='' or str(last_name_entry.get()).isspace()==True or last_name_entry.get()=='' or str(email_entry.get()).isspace()==True or email_entry.get()=='' or str(user_name_entry.get()).isspace()==True or user_name_entry.get()=='' or str(pass_word_entry.get()).isspace()==True or pass_word_entry.get()=='':
            messagebox.showinfo('Fill up', 'Fill up all the information!')
        
        else:
            # connecting to the database file
            conn = sqlite3.connect('accounts_3.db')
            c = conn.cursor() # creating a cursor
            c.execute("SELECT * FROM accounts WHERE username=?",(user_name_entry.get(),))


            if (c.fetchone()==None):
                #executing; inserting the values
                c.execute("INSERT INTO accounts VALUES (:first, :last, :username, :email, :password)",
                {'first': first_name_entry.get(), 'last': last_name_entry.get(), 'username': user_name_entry.get(), 'email': email_entry.get(), 'password': pass_word_entry.get()})
                conn.commit()
                conn.close()
                first_name_entry.delete(0, END)
                last_name_entry.delete(0, END)
                email_entry.delete(0, END)
                user_name_entry.delete(0, END)
                pass_word_entry.delete(0, END)
                transition()

            else:
                messagebox.showinfo("Alert", "Username has already been taken!")
                user_name_entry.delete(0, END)



       

def changeOfficialInfo(use_name):
    official_window = Tk()
    official_window.geometry('500x500')
    official_window.title('Information')
    
    pass

def changeUsername(first_, last_, user_, pass_):
    
    another_window.destroy()
    # creat a window and take user input of new user name
    global user_window
    user_window = Tk()
    user_window.geometry('300x210')
    user_window.title('Change username')
    
    def updateUsername():
        # update the input username in the database
        make_connection = sqlite3.connect('accounts_3.db')
        make_cursor = make_connection.cursor()

        make_cursor.execute("""UPDATE accounts SET username=? WHERE first=? AND last=? AND password=?""", (new_username_entry.get(), first_, last_, pass_))
        
        make_connection.commit()
        make_connection.close()
    #blank label
    label_blank = Label(user_window, text='')
    label_blank.grid(row=0, column=0, pady=10)

    # New username label
    new_username_label = Label(user_window, text='New Username')
    new_username_label.grid(row=1, column=0, padx=20, pady=10)
    new_username_entry = Entry(user_window, width=25)
    new_username_entry.grid(row=1, column=1, padx=5, pady=10)

    #another blank
    label_blank_2 = Label(user_window, text='')
    label_blank_2.grid(row=2, column=0, columnspan=2)

    # submit button
    Submit_Button = Button(user_window, text='Change', command=updateUsername)
    Submit_Button.grid(row=3, column=0, columnspan=2, padx=20, ipadx=100)

    # update the input username in the database

    #make_connection = sqlite3.connect('accounts_3.db')
    #make_cursor = make_connection.cursor()
    #
    #make_cursor.execute('SELECT * FROM accounts WHERE first=?, last=?, password=?', (first_, last_, pass_))
    #change_user_name = make_cursor.fetchone()

    


def Phase(f_name, l_name, use_name, Password):

    global another_window
    another_window = Tk()
    another_window.geometry('280x300')
    
    # Adding a blank label
    def getInfo():
        opendatabase = sqlite3.connect('accounts_3.db')
        point = opendatabase.cursor()
        point.execute("SELECT * FROM accounts WHERE username=?",(use_name,))
        data = point.fetchone()
        opendatabase.commit()
        opendatabase.close()

        if ask_password_entry.get() == data[4]:
            changeUsername(f_name, l_name, use_name, Password)
        else:
            print('not ok')

    blank_ = Label(another_window, text='')

    alert_label = Label(another_window, text='For security purpose')
    alert_label_2 =Label(another_window, text='We need you to enter your password')

    ask_password_label = Label(another_window, text='Password:')
    ask_password_entry = Entry(another_window, show='*', width=25)

    # adding another blank label
    blank_2_ = Label(another_window, text='')

    Submit_ = Button(another_window, text='Submit', command=getInfo)
    
    blank_.grid(row=0, column=0, columnspan=2, pady=8)
    alert_label.grid(row=1, column=0, columnspan=2, padx=30)
    alert_label_2.grid(row=2, column=0, columnspan=2, padx=24)
    ask_password_label.grid(row=3, column=0, pady=15, padx=6)
    ask_password_entry.grid(row=3, column=1, pady=15)

    blank_2_.grid(row=4, column=0, columnspan=2, pady=30)
    Submit_.grid(row=5, column=0, columnspan=2, padx=10, ipadx=100)
    another_window.mainloop()
    


def changeName(use_name, frame4):
    new_window = Tk()
    new_window.title('Change your first and last name')
    new_window.geometry('345x420')
    #new_window.configure(background='white')

    def UpdateData():
        
        if str(f_name_entry.get()).isspace()==True or f_name_entry.get()=='' or str(l_name_entry.get()).isspace()==True or l_name_entry.get()=='':
            messagebox.showinfo('Entries Blank!', 'Fill Out The Entries To Update Your Name')
        
        else:   
            ct = sqlite3.connect('accounts_3.db')
            cr = ct.cursor()
            cr.execute("""UPDATE accounts SET first=?, last=? WHERE username=?""",(f_name_entry.get(), l_name_entry.get(), use_name))
            ct.commit()

            # Changing into the updated name:

            cr.execute("SELECT * FROM accounts WHERE username=?", (use_name,))
            update_name = cr.fetchone()

            ct.commit()
            ct.close()
            update_name_first = update_name[0]
            update_name_last = update_name[1]
            label_ = Label(frame4, text=update_name_first + ' ' + update_name_last)
            label_.grid(row=1, column=0)
        
    # Placing blank labels

    b_1 = Label(new_window, text='')
    
    f_name_label = Label(new_window, text='First Name', bg='green', fg='white', font='9')
    l_name_label = Label(new_window, text='Last Name', bg='green', fg='white', font='9' )
    f_name_entry = Entry(new_window, font='9', width=21)
    l_name_entry = Entry(new_window, font='9', width=21)
    submit = Button(new_window, text='Submit Changes', command=UpdateData)

    

    b_1.grid(row=1, column=0, pady=70)
    f_name_label.grid(row=1, column=0, pady=20, padx=15)
    f_name_entry.grid(row=1, column=1, pady=20)
    l_name_label.grid(row=2, column=0, padx=15)
    l_name_entry.grid(row=2, column=1)
    submit.grid(row=3, column=0, columnspan=2, padx=12, pady=40, ipadx=100)
    new_window.mainloop()
    


def account_access(name):

    root.destroy()
    global personal
    personal = Tk()
    personal.title('Welcome ' + name)
    personal.geometry('530x670')
    usage = PersonalAccount(personal, name)
    personal.mainloop()

def accountWindow(m):
    account_access(m)

def signUp():
    global shoot
    shoot = Tk()
    shoot.title('Register')
    shoot.geometry('500x500')
    shoot.iconbitmap('D:/Icons/star.ico')
    f = Registration(shoot)
    shoot.mainloop()

def main():
    global root
    root = Tk()
    root.title('SIGN IN')
    root.geometry('400x600')
    root.iconbitmap('D:/Icons/star.ico')
    e = Login(root)
    root.mainloop()

def transitionTwo():
    tran.destroy()
    shoot.destroy()
    main()

def transition():
    global tran
    tran = Tk()
    tran.title('Congratulations!')
    tran.geometry('600x450')
    def goToMain():
        transitionTwo()
    l = Label(tran, text='Your new account has been successfully created!')
    l_2 = Label(tran, text='You can now log in new your using the username and password')
    b = Button(tran, text='Okay', command=goToMain)
    l.pack()
    l_2.pack()
    b.pack()

if __name__ == '__main__':
    main()