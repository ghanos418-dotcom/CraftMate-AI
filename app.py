import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, urllib.request, urllib.error, threading

APP = "CraftMate AI"
CFG = os.path.join(os.path.expanduser("~"), ".craftmate_ai.json")
RECIPES = {
 "Crafting Table":("4 planks","P P\nP P"), "Chest":("8 planks","PPP\nP_P\nPPP"),
 "Furnace":("8 cobblestone","CCC\nC_C\nCCC"), "Torch":("coal + stick","C\nS"),
 "Stick":("2 planks","P\nP"), "Bread":("3 wheat","WWW"),
 "Iron Pickaxe":("3 iron ingots + 2 sticks","III\n_S_\n_S_"),
 "Diamond Pickaxe":("3 diamonds + 2 sticks","DDD\n_S_\n_S_"),
 "Iron Sword":("2 iron ingots + stick","I\nI\nS"), "Shield":("6 planks + iron ingot","PIP\nPPP\n_S_"),
 "Bucket":("3 iron ingots","I_I\n_I_"), "Paper":("3 sugar cane","SSS"),
 "Glass Pane":("6 glass","GGG\nGGG"), "Bed":("3 wool + 3 planks","WWW\nPPP")
}
BLUEPRINTS = {
 "Starter House": {"description":"Compact 7x5 survival starter home","layers":[
  [["plank"]*7,["plank","log","log","log","log","log","plank"],["plank","log","air","air","air","log","plank"],["plank","log","air","air","air","log","plank"],["plank","log","log","door","log","log","plank"]],
  [["plank"]*7,["log","air","glass","air","glass","air","log"],["log","air","air","air","air","air","log"],["log","air","air","air","air","air","log"],["log","air","air","air","air","air","log"]],
  [["stairs"]*7 for _ in range(5)]
 ]},
 "Watchtower":{"description":"7x7 watchtower base","layers":[[["stone"]*7 for _ in range(7)],[["cobble","glass","glass","glass","glass","glass","cobble"],["glass","air","air","air","air","air","glass"],["glass","air","air","ladder","air","air","glass"],["glass","air","air","air","air","air","glass"],["glass","air","air","air","air","air","glass"],["cobble","glass","glass","glass","glass","glass","cobble"]],[["plank"]*7 for _ in range(7)]]}
}
def cfg_load():
 try:
  with open(CFG,encoding="utf8") as f:return json.load(f)
 except:return {"api_key":"","model":"gpt-4.1-mini"}
def chunk(x,z):
 cx,cz=x//16,z//16
 return cx,cz,x-cx*16,z-cz*16,cx//32,cz//32
def slime(seed,cx,cz):
 v=(seed+cx*cx*0x4C1906+cx*0x5AC0DB+cz*cz*0x4307A7+cz*0x5F24F)^0x3AD8025F
 s=(v^0x5DEECE66D)&((1<<48)-1); s=(s*0x5DEECE66D+0xB)&((1<<48)-1)
 bits=s>>17
 return bits%10==0

class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title(APP); self.geometry("1050x700"); self.minsize(850,570); self.configure(bg="#0b1017")
  self.cfg=cfg_load(); self.bp=None
  style=ttk.Style(self); style.theme_use("clam")
  style.configure("TFrame",background="#0b1017"); style.configure("TLabel",background="#0b1017",foreground="#e6edf3",font=("Segoe UI",10))
  style.configure("Title.TLabel",font=("Segoe UI",22,"bold"),foreground="#7dd3fc")
  style.configure("TButton",padding=7,background="#1e293b",foreground="#f8fafc")
  style.configure("TNotebook",background="#0b1017"); style.configure("TNotebook.Tab",padding=(14,8),background="#1e293b",foreground="#e6edf3")
  head=ttk.Frame(self,padding=14); head.pack(fill="x"); ttk.Label(head,text="CraftMate AI",style="Title.TLabel").pack(side="left")
  ttk.Label(head,text="Minecraft desktop companion",).pack(side="left",padx=14)
  ttk.Button(head,text="Settings",command=self.settings).pack(side="right")
  self.nb=ttk.Notebook(self); self.nb.pack(fill="both",expand=True,padx=12,pady=(0,12))
  self.make_chunks(); self.make_recipes(); self.make_blueprints(); self.make_ai()
 def page(self,name):
  f=ttk.Frame(self.nb,padding=16); self.nb.add(f,text=name); return f
 def make_chunks(self):
  p=self.page("Seed & Chunks"); ttk.Label(p,text="Chunk coordinate and Java slime-chunk tools",style="Title.TLabel").pack(anchor="w",pady=(0,14))
  row=ttk.Frame(p); row.pack(anchor="w")
  self.seed=tk.StringVar(value=""); self.x=tk.StringVar(value="0"); self.z=tk.StringVar(value="0")
  for label,var,width in [("World seed",self.seed,24),("Block X",self.x,12),("Block Z",self.z,12)]:
   ttk.Label(row,text=label).pack(side="left",padx=(0,4)); ttk.Entry(row,textvariable=var,width=width).pack(side="left",padx=(0,14))
  ttk.Button(row,text="Inspect",command=self.inspect).pack(side="left")
  self.chunkout=tk.Text(p,height=5,bg="#111b27",fg="#e6edf3",relief="flat"); self.chunkout.pack(fill="x",pady=12)
  bar=ttk.Frame(p); bar.pack(fill="x"); ttk.Label(bar,text="Slime scan radius (chunks)").pack(side="left")
  self.radius=tk.StringVar(value="5"); ttk.Entry(bar,textvariable=self.radius,width=5).pack(side="left",padx=8)
  ttk.Button(bar,text="Scan",command=self.scan).pack(side="left")
  self.grid=tk.Text(p,bg="#111b27",fg="#86efac",font=("Consolas",11),relief="flat"); self.grid.pack(fill="both",expand=True,pady=10)
 def inspect(self):
  try:
   x,z=int(float(self.x.get())),int(float(self.z.get())); cx,cz,lx,lz,rx,rz=chunk(x,z)
   self.chunkout.delete("1.0","end"); self.chunkout.insert("end",f"Block ({x}, {z})\nChunk ({cx}, {cz}) • local ({lx}, {lz})\nRegion (.mca) ({rx}, {rz})\nChunk bounds X {cx*16}..{cx*16+15}, Z {cz*16}..{cz*16+15}")
  except ValueError: messagebox.showerror("Invalid coordinates","X and Z must be numbers.")
 def scan(self):
  try:
   seed=int(self.seed.get().strip()); cx,cz,_,_,_,_=chunk(int(float(self.x.get())),int(float(self.z.get()))); r=max(1,min(15,int(self.radius.get())))
   out=""; n=0
   for z in range(cz-r,cz+r+1):
    line=""
    for x in range(cx-r,cx+r+1):
     s=slime(seed,x,z); n+=s; line+= " S " if s else " · "
    out+=line+"\n"
   self.grid.delete("1.0","end"); self.grid.insert("end",out+f"\n{n} slime chunks in {(2*r+1)**2} chunks.")
  except ValueError: messagebox.showerror("Input required","Enter an integer world seed and valid coordinates.")
 def make_recipes(self):
  p=self.page("Recipes"); ttk.Label(p,text="Recipe Explorer",style="Title.TLabel").pack(anchor="w",pady=(0,12))
  self.rsearch=tk.StringVar(); ent=ttk.Entry(p,textvariable=self.rsearch); ent.pack(fill="x"); ent.bind("<KeyRelease>",lambda e:self.refresh_recipes())
  body=ttk.Frame(p); body.pack(fill="both",expand=True,pady=10)
  self.rlist=tk.Listbox(body,bg="#111b27",fg="#e6edf3",selectbackground="#075985",width=28); self.rlist.pack(side="left",fill="y")
  self.rdetail=tk.Text(body,bg="#111b27",fg="#e6edf3",relief="flat",font=("Consolas",12)); self.rdetail.pack(side="left",fill="both",expand=True,padx=(10,0))
  self.rlist.bind("<<ListboxSelect>>",self.recipe_detail); self.refresh_recipes()
 def refresh_recipes(self):
  self.rlist.delete(0,"end")
  for name in RECIPES:
   if self.rsearch.get().lower() in name.lower(): self.rlist.insert("end",name)
 def recipe_detail(self,event=None):
  sel=self.rlist.curselection()
  if not sel:return
  name=self.rlist.get(sel[0]); ing,pat=RECIPES[name]; self.rdetail.delete("1.0","end"); self.rdetail.insert("end",f"{name}\n\nIngredients: {ing}\n\nCrafting pattern:\n{pat}\n\nRecipes can vary by Minecraft edition/version.")
 def make_blueprints(self):
  p=self.page("Blueprints"); ttk.Label(p,text="Blueprint Builder",style="Title.TLabel").pack(anchor="w",pady=(0,12))
  row=ttk.Frame(p); row.pack(fill="x")
  self.bpname=tk.StringVar(value="Starter House"); ttk.Combobox(row,textvariable=self.bpname,values=list(BLUEPRINTS),state="readonly",width=20).pack(side="left")
  ttk.Button(row,text="Load",command=self.load_bp).pack(side="left",padx=6); ttk.Button(row,text="Import JSON",command=self.import_bp).pack(side="left"); ttk.Button(row,text="Export JSON",command=self.export_bp).pack(side="left",padx=6)
  self.layer=tk.IntVar(value=0); ttk.Label(row,text="Layer (0-based)").pack(side="left",padx=(18,4)); ttk.Spinbox(row,from_=0,to=50,textvariable=self.layer,width=5,command=self.draw_bp).pack(side="left")
  self.bpview=tk.Text(p,bg="#111b27",fg="#bbf7d0",font=("Consolas",13),relief="flat"); self.bpview.pack(fill="both",expand=True,pady=12); self.load_bp()
 def load_bp(self):
  self.bp={"name":self.bpname.get(),**BLUEPRINTS[self.bpname.get()]}; self.layer.set(0); self.draw_bp()
 def draw_bp(self):
  if not self.bp:return
  layers=self.bp.get("layers",[])
  if not layers:return
  i=max(0,min(int(self.layer.get()),len(layers)-1)); self.layer.set(i)
  symbols={"air":"·","plank":"P","log":"L","stone":"S","cobble":"C","glass":"G","door":"D","stairs":"/","ladder":"H"}
  grid=layers[i]; counts={}
  text=f"{self.bp.get('name')} — Layer {i+1}/{len(layers)}\n{self.bp.get('description','')}\n\n"
  for row in grid:
   text+=" ".join(symbols.get(b,b[:1].upper()) for b in row)+"\n"
   for b in row:
    if b!="air":counts[b]=counts.get(b,0)+1
  text+="\nBlocks on this layer:\n"+"\n".join(f"{k}: {v}" for k,v in sorted(counts.items()))
  self.bpview.delete("1.0","end"); self.bpview.insert("end",text)
 def import_bp(self):
  path=filedialog.askopenfilename(filetypes=[("Blueprint JSON","*.json")])
  if not path:return
  try:
   with open(path,encoding="utf8") as f:self.bp=json.load(f)
   self.bpname.set(self.bp.get("name","Imported")); self.layer.set(0); self.draw_bp()
  except Exception as e:messagebox.showerror("Import failed",str(e))
 def export_bp(self):
  if not self.bp:return
  path=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("Blueprint JSON","*.json")],initialfile=self.bp.get("name","blueprint").replace(" ","_")+".json")
  if path:
   with open(path,"w",encoding="utf8") as f:json.dump(self.bp,f,indent=2)
   messagebox.showinfo("Saved","Blueprint exported.")
 def make_ai(self):
  p=self.page("AI Assistant"); ttk.Label(p,text="CraftMate AI Assistant",style="Title.TLabel").pack(anchor="w")
  self.chat=tk.Text(p,bg="#111b27",fg="#e6edf3",relief="flat",wrap="word"); self.chat.pack(fill="both",expand=True,pady=10)
  self.chat.insert("end","CraftMate: Ask about Minecraft builds, recipes, commands, survival plans, or chunk tools.\n\n")
  row=ttk.Frame(p); row.pack(fill="x"); self.question=tk.StringVar()
  ent=ttk.Entry(row,textvariable=self.question); ent.pack(side="left",fill="x",expand=True); ent.bind("<Return>",lambda e:self.ask())
  ttk.Button(row,text="Send",command=self.ask).pack(side="left",padx=6)
 def ask(self):
  q=self.question.get().strip()
  if not q:return
  self.question.set(""); self.chat.insert("end",f"You: {q}\n")
  key=self.cfg.get("api_key","")
  if not key:
   ans="Local mode: use the Seed & Chunks, Recipes, and Blueprints tabs for offline tools. Add an API key in Settings for online conversational AI."
   self.chat.insert("end",f"CraftMate: {ans}\n\n"); return
  self.chat.insert("end","CraftMate: thinking...\n"); self.chat.see("end")
  def work():
   try:
    payload=json.dumps({"model":self.cfg.get("model","gpt-4.1-mini"),"instructions":"You are CraftMate, a practical Minecraft assistant. Be concise and don't invent version-specific recipes.","input":q}).encode()
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=payload,headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r: body=json.loads(r.read().decode())
    ans=body.get("output_text","No text returned.")
   except Exception as e:ans="AI error: "+str(e)
   self.after(0,lambda:self.chat.insert("end",f"{ans}\n\n"))
  threading.Thread(target=work,daemon=True).start()
 def settings(self):
  win=tk.Toplevel(self); win.title("CraftMate Settings"); win.geometry("520x260"); win.configure(bg="#0b1017")
  ttk.Label(win,text="OpenAI API key (stored in your Windows user profile)").pack(anchor="w",padx=14,pady=(16,4))
  key=tk.StringVar(value=self.cfg.get("api_key","")); ttk.Entry(win,textvariable=key,show="•").pack(fill="x",padx=14)
  ttk.Label(win,text="Model").pack(anchor="w",padx=14,pady=(10,4))
  model=tk.StringVar(value=self.cfg.get("model","gpt-4.1-mini")); ttk.Entry(win,textvariable=model).pack(fill="x",padx=14)
  def save():
   self.cfg.update({"api_key":key.get().strip(),"model":model.get().strip() or "gpt-4.1-mini"})
   with open(CFG,"w",encoding="utf8") as f:json.dump(self.cfg,f,indent=2)
   win.destroy(); messagebox.showinfo("Saved","Settings saved locally.")
  ttk.Button(win,text="Save",command=save).pack(anchor="e",padx=14,pady=14)

if __name__=="__main__":
 App().mainloop()
