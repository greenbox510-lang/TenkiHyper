fetch("/api/quiz")
  .then(res => res.json())
  .then(data => {
    console.log("DEBUG:", data); // 確認用
    document.getElementById("character").src = "/static/images/" + data.character_image;
  });
