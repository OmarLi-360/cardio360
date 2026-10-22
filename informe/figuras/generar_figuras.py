import json, logging, numpy as np, matplotlib
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import os; B=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(B,"..","..","resultados")+"/"; O=B+"/"
eda=json.load(open(R+"eda.json")); mod=json.load(open(R+"modelos.json")); lat=json.load(open(R+"latente.json"))
plt.rcParams.update({"font.family":["Carlito","Calibri","DejaVu Sans"],"font.size":10,"axes.spines.top":False,"axes.spines.right":False,
 "axes.edgecolor":"#bdb6b3","axes.labelcolor":"#55504f","xtick.color":"#55504f","ytick.color":"#55504f",
 "axes.grid":True,"grid.color":"#ece8e6","grid.linewidth":0.8,"axes.axisbelow":True,"figure.dpi":200,"savefig.bbox":"tight"})
INK="#1c1a1a"; MUT="#857e7c"; SIN="#2a78d6"; CON="#d95926"
MC={"Regresión logística":"#199e70","Random Forest":"#d95926","XGBoost":"#2a78d6"}
MODS=list(MC)
def title(ax,t): ax.set_title(t,loc="left",fontsize=11,color=INK,fontweight="bold",pad=8)

# F1 prevalencia por presión y edad
fig,axs=plt.subplots(1,2,figsize=(9,3.4),gridspec_kw={"width_ratios":[5,6]})
for ax,key,ttl in [(axs[0],"categoria_pa","Por categoría de presión (ACC/AHA 2017)"),(axs[1],"grupo_edad","Por grupo de edad (años)")]:
    p=eda["prevalencia"][key]; x=np.arange(len(p["nivel"])); t=np.array(p["tasa"])*100
    ax.bar(x,t,width=0.66,color=CON)
    for i,v in enumerate(t): ax.text(i,v+1.5,f"{v:.0f} %",ha="center",fontsize=9,color=INK)
    lab=[l.replace("HTA estadio","HTA") .replace("Crisis hipertensiva","Crisis") for l in p["nivel"]]
    ax.set_xticks(x,[f"{l}\nn={n:,}".replace(",",".") for l,n in zip(lab,p["n"])],fontsize=8)
    ax.axhline(49.5,ls="--",lw=1,color=MUT); ax.set_ylim(0,95); ax.set_yticks([0,25,50,75]); ax.yaxis.set_major_formatter(lambda v,_:f"{v:.0f} %")
    ax.grid(axis="x",visible=False); title(ax,ttl)
axs[0].text(-0.4,51.5,"promedio 49 %",ha="left",fontsize=8,color=MUT)
fig.savefig(O+"fig1_prevalencia.png"); plt.close()

# F2 curvas de validación ; F3 curvas de aprendizaje
def curvas(key,fname,xlab):
    fig,axs=plt.subplots(1,3,figsize=(9.6,3.1),sharey=True)
    for ax,m in zip(axs,MODS):
        c=mod[key][m]; x=np.array(c.get("valores",c.get("n")),float)
        for k,ls,lab in [("ent","--","Entrenamiento"),("val","-","Validación")]:
            mu=np.array(c[k+"_media"]); sd=np.array(c[k+"_std"])
            ax.plot(x,mu,ls,color=MC[m],lw=2,label=lab,marker="o",ms=3.5); ax.fill_between(x,mu-sd,mu+sd,color=MC[m],alpha=.12,lw=0)
        if key=="curvas_validacion":
            ax.axvline(c["elegido"],color=MUT,lw=1,ls=":"); 
            if m=="Regresión logística": ax.set_xscale("log")
            ax.set_xlabel(xlab[m],fontsize=8.5)
        else:
            ax.set_xlabel("Pacientes de entrenamiento",fontsize=8.5); ax.xaxis.set_major_formatter(lambda v,_:f"{v/1000:.0f} mil")
        title(ax,m); ax.set_ylim(0.75,1.0)
    axs[0].set_ylabel("AUC-ROC"); axs[0].yaxis.set_major_formatter(lambda v,_:f"{v:.2f}".replace(".",","))
    from matplotlib.lines import Line2D as L2
    axs[0].legend(handles=[L2([],[],ls="--",color="#55504f",lw=2,label="Entrenamiento"),L2([],[],ls="-",color="#55504f",lw=2,label="Validación")]+([L2([],[],ls=":",color=MUT,lw=1,label="Valor elegido")] if key=="curvas_validacion" else []),frameon=False,fontsize=8.5,loc="upper left")
    fig.tight_layout(); fig.savefig(O+fname); plt.close()
curvas("curvas_validacion","fig2_curvas_validacion.png",{"Regresión logística":"C (escala log; menor = más regularización)","Random Forest":"Profundidad máxima","XGBoost":"Profundidad máxima"})
curvas("curvas_aprendizaje","fig3_curvas_aprendizaje.png",None)

# F4 ROC
fig,ax=plt.subplots(figsize=(4.6,4.1))
auc={d["Modelo"]:d["AUC-ROC"] for d in mod["prueba"]}
for m in MODS: ax.plot(mod["roc"][m]["fpr"],mod["roc"][m]["tpr"],color=MC[m],lw=2,label=f"{m} (AUC {auc[m]:.3f})".replace(".",","))
ax.plot([0,1],[0,1],ls="--",color=MUT,lw=1); ax.text(0.62,0.55,"azar (AUC 0,5)",fontsize=8,color=MUT,rotation=40)
ax.xaxis.set_major_formatter(lambda v,_:f"{v:.1f}".replace(".",",")); ax.yaxis.set_major_formatter(lambda v,_:f"{v:.1f}".replace(".",","))
ax.set_xlabel("1 − especificidad (tasa de falsas alarmas)"); ax.set_ylabel("Sensibilidad"); ax.legend(frameon=False,fontsize=8.5,loc="lower right")
ax.set_aspect("equal"); title(ax,"Curvas ROC en prueba (13.703 pacientes)")
fig.savefig(O+"fig4_roc.png"); plt.close()

# F5 SHAP vs coeficientes
sh=mod["importancia"]["shap"]; nom={"sistolica":"Sistólica","edad":"Edad","colesterol_3":"Colesterol muy alto","diastolica":"Diastólica","activo":"Actividad física","colesterol_2":"Colesterol alto","imc":"IMC","peso":"Peso","glucosa_3":"Glucosa muy alta","fuma":"Fuma","altura":"Altura","alcohol":"Alcohol","sexo_hombre":"Sexo (hombre)","glucosa_2":"Glucosa alta"}
k=list(sh)[::-1]; fig,ax=plt.subplots(figsize=(5.6,3.9))
ax.barh([nom[i] for i in k],[sh[i] for i in k],color="#2a78d6",height=0.62)
for i,v in enumerate([sh[i] for i in k]): ax.text(v+0.01,i,f"{v:.2f}".replace(".",","),va="center",fontsize=8,color=INK)
ax.set_xlabel("|SHAP| medio (log-odds)"); ax.xaxis.set_major_formatter(lambda v,_:f"{v:.1f}".replace(".",",")); ax.grid(axis="y",visible=False); title(ax,"Importancia de las variables · XGBoost")
fig.savefig(O+"fig5_shap.png"); plt.close()

# F6 PCA y UMAP
real=np.array(lat["real"]); fig,axs=plt.subplots(1,2,figsize=(9,3.9))
rng=np.random.default_rng(42); idx=rng.permutation(len(real))
for ax,m in zip(axs,["PCA","UMAP"]):
    C=np.array(lat["coords"][m])[idx]; r=real[idx]
    ax.scatter(C[:,0],C[:,1],s=5,c=np.where(r==1,CON,SIN),alpha=.55,lw=0)
    q=lat["calidad"][m]; title(ax,f"{m} · confiabilidad {q['confiabilidad']:.2f} · AUC k-NN {q['auc_knn']:.2f}".replace(".",","))
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    ax.set_xlabel("PC1" if m=="PCA" else "UMAP 1",fontsize=8.5); ax.set_ylabel("PC2" if m=="PCA" else "UMAP 2",fontsize=8.5)
from matplotlib.lines import Line2D
axs[1].legend(handles=[Line2D([],[],marker="o",ls="",color=SIN,label="Sin ECV"),Line2D([],[],marker="o",ls="",color=CON,label="Con ECV")],frameon=False,fontsize=9,loc="upper right")
fig.tight_layout(); fig.savefig(O+"fig6_pca_umap.png"); plt.close()
print("ok")
