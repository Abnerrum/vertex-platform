const titles={dashboard:"Visão geral",clientes:"Clientes",projetos:"Projetos",servicos:"Serviços / OS",roadmap:"Roadmap"};
document.querySelectorAll("nav button").forEach(btn=>btn.addEventListener("click",()=>{
 document.querySelectorAll("nav button").forEach(b=>b.classList.remove("active"));
 document.querySelectorAll(".page").forEach(p=>p.classList.remove("show"));
 btn.classList.add("active");
 const id=btn.dataset.page;
 document.getElementById(id).classList.add("show");
 document.getElementById("title").textContent=titles[id];
}));
document.querySelectorAll(".primary").forEach(b=>b.addEventListener("click",()=>alert("Funcionalidade prevista para a próxima etapa do MVP.")));