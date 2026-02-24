const tbody = document.getElementById("tbody");

document.getElementById("form").addEventListener("submit", async e=>{
    e.preventDefault();
    await fetch("/add_transaction",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            date:date.value,
            category:category.value,
            description:description.value,
            amount:amount.value,
            type:type.value
        })
    });
    load();
});

async function load(){
    let data = await fetch("/transactions").then(r=>r.json());
    tbody.innerHTML="";
    data.forEach(t=>{
        tbody.innerHTML+=`
        <tr>
        <td>${t.date}</td>
        <td>${t.category}</td>
        <td>${t.description}</td>
        <td>₹${t.amount}</td>
        <td><span class="badge ${t.type=='Income'?'bg-success':'bg-danger'}">${t.type}</span></td>
        <td>
            <button class="btn btn-sm btn-warning" onclick='openEdit(${JSON.stringify(t)})'>Edit</button>
            <button class="btn btn-sm btn-danger" onclick='del(${t.id})'>Delete</button>
        </td>
        </tr>`;
    });
}

function del(id){
    fetch(`/delete_transaction/${id}`,{method:"DELETE"}).then(load);
}

function openEdit(t){
    editId.value=t.id;
    editDate.value=t.date;
    editDesc.value=t.description;
    editAmount.value=t.amount;
    new bootstrap.Modal(editModal).show();
}

function updateTransaction(){
    fetch(`/edit_transaction/${editId.value}`,{
        method:"PUT",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            date:editDate.value,
            category:"Others",
            description:editDesc.value,
            amount:editAmount.value,
            type:"Expense"
        })
    }).then(()=>{load(); location.reload();});
}

load();

// Reminder every 60 seconds (demo)
setInterval(()=>{
    alert("⏰ Don’t forget to update your expenses!");
},60000);
