import os

class Tag(object):
    def __init__(self,name,**kwargs):
        self.name = name
        self.attrs = kwargs
        self.contents = []
        
    def add(self,*args):
        if len(args) > 0:
            self.contents += args
        
    def __str__(self):
        attr_str = ' '.join([k+'="'+str(v)+'"' for k,v in self.attrs.items()])
        def make_tag(name,attrs):
            if len(attrs) == 0:
                return "<{0}>".format(name)
            else:
                return "<{0} {1}>".format(name,attrs)
        if len(self.contents) == 0:
            return make_tag(self.name,attr_str)
        else:
            start_tag = make_tag(self.name,attr_str)
            end_tag = "</{0}>".format(self.name)
            return (start_tag + 
                    "".join([str(x) for x in self.contents]) +
                    end_tag)


class Table(object):
    def __init__(self,**kwargs):
        self.table = Tag("table",**kwargs)
        self.cursor = self.table
        
    def start_row(self,**kwargs):
        row = Tag("tr",**kwargs)
        self.table.add(row)
        self.cursor = row
        
    def end_row(self):
        self.cursor = self.table
        
    def add_cell(self,*args,**kwargs):
        col = Tag("td",**kwargs)
        col.add(*args)
        self.cursor.add(col)
        
    def __str__(self):
        return str(self.table)

def table_from_tuples(tuples,header,display=None):
    if display:
        display = [(f if f else lambda x:x) for f in display]
    table = Table()
    table.start_row()
    for h in header:
        table.add_cell("<b>{0}</b>".format(h))
    table.end_row()
    for tup in tuples:
        if display:
            tup = [f(x) for f,x in zip(display,tup)]
        table.start_row()
        for s in tup:
            table.add_cell(str(s))
        table.end_row()
    return table

class Form(object):
    def __init__(self,action,method="post"):
        self.text = '<form action="{0}" method="{1}">'.format(action,method)
        
    def add_hidden(self,name,value):
        html = '<input type="hidden" name="{0}" value="{1}">'
        self.text += html.format(name,value)
    
    def add_text_field(self,name,caption,default=""):
        html = '{0}  <input type="text" name={1} value={2}>'
        self.text += html.format(caption,name,default)
    
    def add_checkbox(self,name,caption,checked=False):
        html = '{0} <input type="checkbox" name="{1}" value="T" checked="{2}">'
        self.text += html.format(caption,name,checked)
    
    def add_return(self):
        self.text += "<br>"
    
    def add_submit(self,caption="Submit"):
        self.text += '<input type="submit" value="{0}">'.format(caption)
    
    def __str__(self):
        return self.text + "</form>"
    
def h2(text):
    return "<h2>{0}</h2>".format(text)     

def image(picPath,height):
	data_uri = open(picPath, 'rb').read().encode('base64').replace('\n', '')
	img_tag = '<img src="data:image/jpeg;base64,{0}" height=\"{1}\">'.format(data_uri,height)
	return img_tag
	
def imageLink(picPath,height):
	data_uri = open(picPath, 'rb').read().encode('base64').replace('\n', '')
	img_tag = '<img src="data:image/jpeg;base64,{0}" height=\"{1}\">'.format(data_uri,height)
	link_tag = '<a href=\"data:image/jpeg;base64,{0}\">\n'.format(data_uri) + img_tag + '\n</a>' 
	return link_tag
	
# Directory of graphs is passed into function
# The function plots an 8x12 table of graphs
def tableFromImageDir(dirName):
	fileList = sorted(os.listdir(dirName))
	rows = ['A','B','C','D','E','F','G','H']
	table_string = "<table border=\"1\">"
	k = 0; # Keeps track of which graph/image to post next
	for j in range(9):
		# Start row
		table_string += "<tr>"
		for i in range(13):	
			if j == 0 and i == 0:
				table_string += "<td></td>"
			if j == 0 and i != 0:
				table_string += "<td>"
				table_string += str(i)
				table_string += "</td>"
			if j != 0 and i == 0:
				table_string += "<td>"
				table_string += rows[j - 1]
				table_string += "</td>"
			# Fill cell
			if j > 0 and i > 0:
				file = fileList[k]
				if file != "plate.jpg":
					k = k + 1;
					imageName = os.path.join(dirName,file)
					table_string += "<td>"
					table_string += imageLink(imageName,50)
					table_string += "</td>\n"
		# End row
		table_string += "</tr>\n"
	table_string += "</table>\n"
	return table_string;

if __name__ == '__main__':
    tag = Tag("table",height=3)
    tag.add(Tag("tr"))
    tag.add("content, and more content")
    print tag
    
    tab = Table(height=3)
    tab.start_row()
    tab.add_cell("content, and more content")
    tab.end_row()
    print tab
