import flet as ft
import sqlite3
import datetime

class ToDo:
     #é uma funcção iniciada junto com a inicialização da aplicação
    def __init__(self, page: ft.Page):
        #configurações iniciais da Página
        self.page = page
        self.page.bgcolor = ft.colors.WHITE
        self.page.window_width = 400
        self.page.window_height = 450
        self.page.window_resizable = False
        self.page.window_always_on_top = True
        self.page.title = 'Aplicativo de Tarefas'
        self.task = ''
        self.view = 'all'
        
        # Inicialização do banco de dados SQLite e recuperação de Tarefas
        self.db_execute("CREATE TABLE IF NOT EXISTS tasks(name, status)")
        self.results = self.db_execute('SELECT * FROM tasks')

        # Confuguração da Página inicial
        self.main_page()

    #Função para executar consultas no BD
    def db_execute(self, query, params = []):
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute(query, params)
            con.commit()
            return cur.fetchall() 
            # retorna todas as linhas
            #o comando with abre a conexão com o BD, executa todo o código e depois fecha o BD

    # Funçã para definir o valor da terefa
    def set_value(self, e):
        self.task = e.control.value

    # Função para adinionar uma nova tarefa
    def add(self, e, input_task):
        name = self.task
        status ='incomplete'

        if name:
            self.db_execute(query = 'INSERT INTO tasks VALUES(?, ?)', params = [name, status])
            input_task.value = ''
            self.results = self.db_execute('SELECT * FROM tasks')
            self.update_task_list()

    # Função chamada quando uma tarefa é marcada como concluída ou não
    def checked(self, e):
        is_checked = e.control.value
        label = e.control.label

        if is_checked:
            self.db_execute('UPDATE tasks SET status = "complete" WHERE name = ?', params = [label])
        else:
            self.db_execute('UPDATE tasks SET status = "incomplete" WHERE name = ?', params= [label])
        
        if self.view == 'all':
            self.results = self.db_execute('SELECT * FROM tasks')
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params = [self.view])

        self.update_task_list()

    #Função para criar o container de tarefas
    def tasks_container(self):
        return ft.Container(
            height = self.page.height * 0.8,
            content = ft.Column(
                controls = [
                    ft.Checkbox(
                        label = res[0], 
                        on_change = self.checked,
                        value = True if res[1] == 'complete' else False
                        )for res in self.results if res],
                scroll = ft.ScrollMode.ALWAYS        
                )
            )   
    
    # Função para atualizar a lista de tardefas exibida
    def update_task_list(self):
        tasks = self.tasks_container()
        self.page.controls.pop()  
        self.page.add(tasks)
        self.page.update()

    # Função chamada quando as abas de visualização são alteradas
    def tabs_changed(self, e):
        if e.control.selected_index == 0:
            self.results = self.db_execute('SELECT * FROM tasks')
            self.view == 'all'
        elif e.control.selected_index == 1:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "incomplete"')
            self.view == 'incomplete'
        elif e.control.selected_index == 2:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "complete"')
            self.view == 'complete'

        self.update_task_list()
   
   # Função para criar a página principal do Aplicativo
    def main_page(self):
        input_task = ft.TextField(hint_text = 'Digite aqui sua tarefa',expand = True, on_change = self.set_value)
        
        input_bar = ft.Row(
            controls = [
                input_task,
                ft.FloatingActionButton(icon = ft.icons.ADD, on_click = lambda e: self.add(e, input_task))
            ]
        )

        tabs = ft.Tabs(
            selected_index = 0, on_change=self.tabs_changed,
            tabs = [
            ft.Tab(text='Todos'),
            ft.Tab(text='Em Andamento'),
            ft.Tab(text='Finalizado')
            ],
        )

        tasks = self.tasks_container()

        self.page.add(input_bar, tabs, tasks)
    
# Inicialização da Aplicação
ft.app(target = ToDo)