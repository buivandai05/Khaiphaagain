document.addEventListener('DOMContentLoaded', () => {
  const $ = id => document.getElementById(id);
  const selected = new Map();
  let catalog = [];
  const pct = n => `${(Number(n) * 100).toFixed(1)}%`;
  const ratingText = value => value === 'high' ? 'Tỷ lệ cao, đủ mẫu' : value === 'potential' ? 'Tiềm năng' : 'Chưa đủ dữ liệu';
  const cell = (row, value) => { const td = row.insertCell(); td.textContent = value; return td; };

  function renderOptions() {
    const q = $('heroSearch').value.trim().toLocaleLowerCase();
    const root = $('heroOptions'); root.replaceChildren();
    catalog.filter(h => !selected.has(h.id) && h.name.toLocaleLowerCase().includes(q)).slice(0, 30).forEach(hero => {
      const button = document.createElement('button'); button.type = 'button'; button.className = 'btn btn-sm btn-outline-secondary me-2 mb-2'; button.textContent = `+ ${hero.name}`;
      button.addEventListener('click', () => { if (selected.size >= 5) return; selected.set(hero.id, hero); renderSelected(); renderOptions(); }); root.append(button);
    });
  }
  function renderSelected() {
    const root = $('selectedHeroes'); root.replaceChildren();
    if (!selected.size) { root.textContent = 'Chưa chọn tướng nào'; return; }
    selected.forEach(hero => {
      const button = document.createElement('button'); button.type = 'button'; button.className = 'btn btn-sm btn-info me-2 mb-1'; button.textContent = `${hero.name} ×`;
      button.title = 'Bấm để bỏ chọn'; button.addEventListener('click', () => { selected.delete(hero.id); renderSelected(); renderOptions(); }); root.append(button);
    });
  }
  async function loadTeams(heroes = []) {
    const query = new URLSearchParams({size: $('teamSize').value, sort: $('teamSort').value, min_matches: $('teamMinMatches').value, heroes: heroes.join(',')});
    const response = await fetch(`/api/team-compositions?${query}`); const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Không thể tải thống kê đội hình.');
    catalog = data.catalog; renderOptions();
    const body = $('teamsBody'); body.replaceChildren();
    if (!data.compositions.length) { const tr = body.insertRow(); const td = tr.insertCell(); td.colSpan = 8; td.className = 'empty-state'; td.textContent = 'Không có tổ hợp nào đạt số trận tối thiểu với bộ lọc này.'; }
    data.compositions.slice(0, 20).forEach(team => {
      const tr = body.insertRow(); cell(tr, team.label); cell(tr, pct(team.win_rate)); cell(tr, String(team.matches)); cell(tr, `${team.wins} / ${team.losses}`);
      cell(tr, pct(team.support)); cell(tr, pct(team.confidence)); cell(tr, Number(team.lift).toFixed(2)); cell(tr, ratingText(team.rating));
    });
    $('teamsInfo').textContent = `${data.total_transactions.toLocaleString()} transaction đội; tỷ lệ thắng chung ${pct(data.overall_win_rate)}. Chỉ hiển thị tối đa 20 đội hình, đã lọc các đội có ít hơn ${$('teamMinMatches').value} trận.`;
    return data;
  }
  function showLookup(team) {
    const root = $('lookupResult'); root.replaceChildren();
    const heading = document.createElement('h5'); heading.textContent = team.label; root.append(heading);
    if (!team.found) { const note = document.createElement('div'); note.className = 'alert alert-warning'; note.textContent = 'Tổ hợp này không xuất hiện trong dữ liệu.'; root.append(note); return; }
    const cards = document.createElement('div'); cards.className = 'row g-2';
    const values = [["Tỷ lệ thắng", pct(team.win_rate)], ["Số trận", team.matches], ["Thắng / Thua", `${team.wins} / ${team.losses}`], ["Support", pct(team.support)], ["Confidence", pct(team.confidence)], ["Lift", Number(team.lift).toFixed(2)]];
    values.forEach(([label, value]) => { const col = document.createElement('div'); col.className = 'col-6 col-lg-2'; const box = document.createElement('div'); box.className = 'stat-card h-100'; const name = document.createElement('div'); name.className = 'stat-label'; name.textContent = label; const number = document.createElement('div'); number.className = 'number'; number.textContent = value; box.append(name, number); col.append(box); cards.append(col); }); root.append(cards);
    const note = document.createElement('p'); note.className = `mt-3 ${team.rating === 'insufficient' ? 'text-warning' : 'text-secondary'}`; note.textContent = team.rating === 'insufficient' ? `Chưa đủ dữ liệu để đánh giá đáng tin cậy (cần ít nhất ${team.min_matches} trận theo ngưỡng đang chọn và tối thiểu 10 trận).` : `${ratingText(team.rating)}. Kết quả mô tả dữ liệu quan sát, không đảm bảo kết quả trận tương lai.`; root.append(note);
  }

  $('heroSearch').addEventListener('input', renderOptions);
  $('refreshTeams').addEventListener('click', async () => { try { await loadTeams(); } catch (e) { $('teamsInfo').textContent = e.message; } });
  ['teamSize', 'teamSort', 'teamMinMatches'].forEach(id => $(id).addEventListener('change', async () => { try { await loadTeams(); } catch (e) { $('teamsInfo').textContent = e.message; } }));
  $('analyzeTeam').addEventListener('click', async () => {
    if (selected.size < 2 || selected.size > 5) { $('lookupResult').textContent = 'Vui lòng chọn từ 2 đến 5 tướng.'; return; }
    try { const data = await loadTeams([...selected.keys()]); showLookup(data.selected); } catch (e) { $('lookupResult').textContent = e.message; }
  });
  loadTeams().catch(e => { $('teamsInfo').textContent = e.message; });
});
