
import os
import sys
import tkinter as Tkinter
import tkinter.filedialog
import traceback
import __main__
import pandas as pd
from Reddit_Scraper.RedditScraper import redditscraper
from LDA.LDA_Infer import lda_infer
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

tkFileDialog = tkinter.filedialog

#Abbreviate
m = __main__

# Create and hide the root window
root = Tkinter.Tk()
root.wm_title("REDDIT_SCRAPER")
root.withdraw()

class gui_interface():

    def __init__(self):
        
        self.Access = 0
        self.gui_window = self._Create_GUI_Window()
        self.credentials = self.__Get_Credentials_File__()
        self.scraper = redditscraper(self.credentials)

        self.LDA = lda_infer(os.path.join('LDA','models','hash_vect.pk'),
                             os.path.join('LDA','models','lda_model_8.pk'))

    def get_topic_predict(self, texts):
        clean_text, pred = self.LDA.infer(texts)
        # print(pred)
        pred =  [np.where(r==r.max())[0][0] for r in pred]
        return clean_text, pred
    
    def __Get_Credentials_File__(self, credentials_file = 'Credentials.txt'):

        # txt_file_path = credentials_file
        
        if not os.path.isfile(credentials_file):
            
            # Where Am I File & Path
            file_path = sys._getframe().f_code.co_filename

            # This Directory
            Dir = os.path.dirname(file_path)

            #Abbreviate
            Select_File = tkFileDialog.askopenfilename

            T = "Select File Path to Credentials.txt"
            F = (("TXT files","*.txt"),("all files","*.*"))
            TF = Select_File(initialdir = Dir, title = T, filetypes = F)
        
            credentials_file = TF

            if 'Credentials.txt' != os.path.basename(credentials_file) or not credentials_file:

                m.CButton.place(x=25,y=531)
                m.CButton.update
            
                msg = "Invalid or Missing Credentials.\n\nPlease update or locate "
                msg += "the Credentials.txt file before using this this API.\n"
                m.textbox.delete(1.0, Tkinter.END)
                m.textbox.insert(1.0, msg )
                m.textbox.configure(fg='red')
                m.textbox.update()

                return
                
        CF = open(credentials_file, 'r')
        CF_Data = CF.read()
        CF.close()

        credentials_dictionary = {}
        
        for Line in CF_Data.splitlines():
            if not Line.strip():
                continue

            Key, Value = Line.split('=')

            credentials_dictionary[Key.strip()] = Value.strip()

        # self.credentials = credentials_dictionary

        # Test credentials
        Test = redditscraper(credentials_dictionary).Get_Reddit_Comments('Politics', 1, 'top')


        if isinstance(Test, pd.DataFrame):
            
            m.CButton.place_forget()

            m.textbox.delete(1.0, Tkinter.END)
            m.textbox.configure(fg='black')
            m.textbox.update()

        else:

            m.CButton.place(x=25,y=531)
            m.CButton.update
            
            msg = "Invalid or Missing Credentials.\n\nPlease update or locate "
            msg += "the Credentials.txt file before using this this API.\n\n"
            msg += Test
            
            m.textbox.delete(1.0, Tkinter.END)
            m.textbox.insert(1.0, msg )
            m.textbox.configure(fg='red')
            m.textbox.update()

        return credentials_dictionary

    
    def _GET_TOPIC(self, e=""):

        self.Access = 0

        self.Topic = m.TBox.get().strip()
        self.Limit = m.LBox.get().strip()

        if not self.Limit or not self.Limit.isdigit() :

            m.LBox.delete(0, Tkinter.END)
            m.LBox.insert(0, "5")
            m.LBox.configure(fg='black')
            m.LBox.update()
            Limit = 5

        self.Limit = int(self.Limit)

        if "Type Sub Reddit Topic Here" in self.Topic or not self.Topic:

            if not self.Topic:
                
                msg = "No Sub Reddit Topic Found in the Entry Box Below"
                m.textbox.delete(1.0, Tkinter.END)
                m.textbox.insert(Tkinter.END, msg)
                
            return

        #Get Subreddit Pre-Check
        # Test_Request = self.scraper.Get_Reddit_Comments(Topic, 1)
        Test_Request = self.scraper.Get_Reddit_Comments(self.Topic, 1, 'top')
        
        if not isinstance(Test_Request, pd.DataFrame):
            
            msg = '\nWeb Access Error.\n'
            msg += 'Please check your Sub_Reddit_Topic. --> '+ self.Topic +'\n'
            msg += 'Server could not understand request due to invalid syntax.'
            msg += repr(Test_Request)
            
            m.textbox.delete(1.0, Tkinter.END)
            m.textbox.insert(1.0, msg )
            m.textbox.configure(fg='red')
            m.textbox.update()
            return

        m.textbox.configure(fg='black')
        m.textbox.delete(1.0, Tkinter.END)

        msg ="\n\nGetting Reddit_Comments. Please Wait . . . \n\n"

        m.textbox.insert(Tkinter.END, msg)
        m.textbox.update()
         
        self.Comments = self.scraper.Get_Reddit_Comments(self.Topic, 
                                    Limit=self.Limit, 
                                    how='asc', 
                                    duration='5y')
        
        # print(Comments)

        m.textbox.delete(1.0, Tkinter.END)
        count = 1
        for title in self.Comments['title']:
            try:
                _, pred = self.get_topic_predict([title])
                m.textbox.insert(Tkinter.END, str(count) + ':  ' )
                m.textbox.insert(Tkinter.END, title[:75] + ' . . . . . ')
                m.textbox.insert(Tkinter.END, str(pred) + ' . ')
                m.textbox.insert(Tkinter.END, '\n')
                m.textbox.update()
                count += 1
            except:
                m.textbox.insert(Tkinter.END, str(count) + ':  ' )
                m.textbox.insert(Tkinter.END, title[:75] + ' . . . . . ')
                m.textbox.insert(Tkinter.END, '[n/a]' + ' . ')
                m.textbox.insert(Tkinter.END, '\n')
                m.textbox.update()
                count += 1
                pass

    def _Get_Credentials(self):

        self.__Get_Credentials_File__("")

    def _Plot_Graphs(self):

        # msg = 'Update code for the   < _Plot_Graphs  >  Method'
        _, pred = self.get_topic_predict(list(self.Comments['title']))
        t = range(len(pred))
        sns.set_style('dark')
        d = sns.displot(pred, bins=8).set(title=f'Distribution of r/{self.Topic} topics\nn={self.Limit}')
        mids = [rect.get_x() + rect.get_width() / 2 for rect in d.ax.patches]
        plt.xticks(ticks =mids, labels= [1,2,3,4,5,6,7,8])
        plt.tight_layout()
        plt.show()



        # m.textbox.delete(1.0, Tkinter.END)
        # m.textbox.insert(1.0, msg )
        # m.textbox.update()

    def _check_tbox_focus(self):

        Topic = m.TBox.get().strip()
        Limit = m.LBox.get().strip()
        
        if "LIMIT" not in Limit and "Type Sub Reddit Topic Here"  not in Topic:
            
            return

        if  'canvas.!entry2>' in repr(m.window.focus_get()):

            if "LIMIT" in m.LBox.get().strip():

                m.LBox.delete(0, Tkinter.END)
                m.LBox.configure(fg='black')

        elif  'canvas.!entry>' in repr(m.window.focus_get()):

            if "Type Sub Reddit Topic Here" in m.TBox.get().strip():

                m.TBox.delete(0, Tkinter.END)
                m.TBox.configure(fg='black')

        elif  'canvas.!button>' in repr(m.window.focus_get()):

            if "Type Sub Reddit Topic Here" in m.TBox.get().strip():

                m.TBox.configure(fg='grey')

            if "LIMIT" in m.LBox.get().strip():

                m.LBox.configure(fg='grey')
                
        m.window.after(500, self._check_tbox_focus)

    def _ButtonPress(self, e=""):

        m.TButton.focus_set()
        m.TButton.update()

    def _ButtonRelease(self, e=""):

        m.TButton.focus_set()
        m.TButton.update()

    def _Create_GUI_Window(self):
    
        window = Tkinter.Toplevel()

        window.configure(background = 'black')
        window.attributes('-topmost', False)
        window.state('zoomed')
        window.resizable(1,1)
    
        window.state('normal')

        width = 800
        height = 600
    
        window.maxsize(width, height)
        window.minsize(width, height)

        canvas = Tkinter.Canvas(window, highlightthickness=0)
        canvas.configure(background = 'white')
        canvas.pack(fill=Tkinter.BOTH, expand=1)
        canvas.update()

        # Create a Grdient Background
        for row in range(0,height)[::-1]:
            r = int(row / (height - 1)*0)
            g = int(row / (height - 1)*0)
            b = int(row / (height - 1)*125)

            canvas.create_line(0,row,width,row, fill = "#%02x%02x%02x" % (r, g, b) )

        canvas2 = Tkinter.Canvas(window, highlightthickness=0)
        canvas2.configure(background = 'white')
        canvas2.place(x=25, y=50)
        canvas2.update()

        textbox = Tkinter.Text(canvas2, relief=Tkinter.RAISED)
        textbox.insert(Tkinter.END, "Type a Sub Reddit Topic in the Entry Box Below.\n")
        textbox.configure(font=("Arial",12))

        textbox.place(x=20, y=50)
        textbox['width'] = 80
        textbox['height'] = 26
        textbox['bg'] =   'white'#'#008800'
        textbox['bd'] = 2
        textbox.update()
    
        scrollbar = Tkinter.Scrollbar(canvas2, orient=Tkinter.VERTICAL, command = textbox.yview )
        textbox['yscroll'] = scrollbar.set
        scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y) #, expand=1)
        textbox.pack(fill=Tkinter.BOTH, expand=Tkinter.Y)

        m.textbox = textbox

        TBox = Tkinter.Entry(canvas, bg='white', width=27)
        __main__.TBox = TBox
        TBox.place(x=79,y=532)
        TBox.configure(font=("Arial",13), fg='light grey')
        TBox.delete(0, Tkinter.END)
        TBox.insert(Tkinter.END, "  Type Sub Reddit Topic Here")

        m.TBox = TBox

        LBox = Tkinter.Entry(canvas, bg='white', width=5)
        __main__.LBox = LBox
        LBox.place(x=25,y=532)
        LBox.configure(font=("Arial",13), fg='light grey')
        LBox.delete(0, Tkinter.END)
        LBox.insert(0, "LIMIT")
        
        m.LBox = LBox

        text = 'GET  SUBREDDIT  TOPIC'
        command = self._GET_TOPIC

        TButton = Tkinter.Button(canvas, width=29, text=text, command=command)
        __main__.TButton = TButton
        TButton.place(x=332,y=531)
        
        TButton.bind('<ButtonPress-1>',self._ButtonPress)
        TButton.bind('<ButtonRelease-1>',self._ButtonRelease)

        text = 'PLOT MATPLOTLIB GRAPHS'
        command = self._Plot_Graphs

        PButton = Tkinter.Button(canvas, width=30, text=text, command=command)
        __main__.PButton = PButton
        PButton.place(x=550,y=531)

        text = 'GET REDDIT CREDENTIALS'
        command = self._Get_Credentials

        CButton = Tkinter.Button(canvas, width=105, text=text, command=command)
        __main__.CButton = CButton
        CButton.place(x=25,y=531)
        
        m.window = window
        self._check_tbox_focus()
        window.update()
        
        

#----------------------------------------------------------------

if __name__ == '__main__':

    app = gui_interface()

    def on_closing():
        m.window.destroy()
        root.destroy()
    m.window.protocol("WM_DELETE_WINDOW", on_closing)
    m.window.mainloop()




      