from pathlib import Path

p = Path('index.html')
t = p.read_text(encoding='utf-8')

if 'id="reviewModal"' in t:
    raise SystemExit(0)

css = r'''
.reviewSummary{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:10px}
.reviewStat{background:#0002;border:1px solid #ffffff16;border-radius:11px;padding:9px;text-align:center}
.reviewStat b{display:block;font-size:20px}.reviewStat span{font-size:11px;color:var(--muted)}
.reviewList{display:grid;gap:8px}
.reviewItem{display:grid;grid-template-columns:72px 1fr auto;gap:10px;align-items:center;text-align:left;background:#0002;color:#fff;border:1px solid #ffffff1b;padding:10px}
.reviewMoveNo{font-size:13px;font-weight:800}.reviewMeta{min-width:0}.reviewMeta b{display:block;font-size:14px}.reviewMeta span{display:block;font-size:12px;color:var(--muted);margin-top:2px}
.reviewItemScore{min-width:54px;text-align:center;background:#fff;color:#173625;border-radius:10px;padding:7px 6px;font-size:19px;font-weight:900}
.reviewHelp{font-size:12px;color:var(--muted);line-height:1.6;margin-bottom:10px}
@media(max-width:520px){.reviewItem{grid-template-columns:62px 1fr auto;gap:7px;padding:9px}.reviewItemScore{min-width:48px;font-size:17px}}
'''
t = t.replace('\n.replayPanel{', '\n' + css + '\n.replayPanel{', 1)

t = t.replace(
    '        <button class="secondary" id="replay" disabled>リプレイを見る</button>\n',
    '        <button class="secondary" id="replay" disabled>リプレイを見る</button>\n'
    '        <button class="secondary" id="review" hidden>対局レビュー</button>\n',
    1,
)

review_html = r'''
<div class="analysisModal" id="reviewModal" role="dialog" aria-modal="true" aria-labelledby="reviewHeading">
  <div class="analysisDialog" id="reviewDialog">
    <div class="analysisHead">
      <h2 id="reviewHeading">対局レビュー</h2>
      <button class="secondary" id="reviewClose">閉じる</button>
    </div>
    <div class="reviewSummary">
      <div class="reviewStat"><b id="reviewAverage">-</b><span>平均点</span></div>
      <div class="reviewStat"><b id="reviewBestCount">-</b><span>最善手</span></div>
      <div class="reviewStat"><b id="reviewImproveCount">-</b><span>要改善</span></div>
    </div>
    <div class="reviewHelp">各着手をタップすると、その手を打つ直前の盤面に戻して、赤枠の実際の手と黄枠の最善手を比較できます。</div>
    <div class="reviewList" id="reviewList"></div>
  </div>
</div>

'''
t = t.replace('\n<script>\nconst N=8,E=0,B=1,W=-1;', '\n' + review_html + '<script>\nconst N=8,E=0,B=1,W=-1;', 1)

t = t.replace(
    '  history:[],replay:null,analysis:null,analysisToken:0\n};',
    '  history:[],replay:null,analysis:null,analysisToken:0,reviews:[],analysisReturnToReview:false\n};',
    1,
)

t = t.replace(
    'function showAnalysisBusy(){',
    '''function hideReview(){
  $('reviewModal').classList.remove('show');
  document.documentElement.classList.remove('analysisOpen');
}
function resetReview(){
  s.reviews=[];s.analysisReturnToReview=false;
  $('review').hidden=true;$('review').textContent='対局レビュー';
  hideReview();
}
function showAnalysisBusy(){''',
    1,
)

t = t.replace(
    "stopReplayTimer();s.replay=null;$('replayPanel').classList.remove('show');hideAnalysis();",
    "stopReplayTimer();s.replay=null;$('replayPanel').classList.remove('show');hideAnalysis();resetReview();",
    1,
)

t = t.replace(
    '    s.analysis=analyzeHumanMove(before,movingCol,r,c);\n    updateAnalysisCard();',
    '    s.analysis=analyzeHumanMove(before,movingCol,r,c);\n    s.analysis.moveNo=s.reviews.length+1;\n    s.reviews.push(s.analysis);\n    updateAnalysisCard();',
    1,
)

t = t.replace(
    'function openAnalysis(){\n  let a=s.analysis;if(!a)return;\n  drawAnalysisBoard(a);',
    "function openAnalysis(){\n  let a=s.analysis;if(!a)return;\n  $('analysisClose').textContent=s.analysisReturnToReview?'レビューに戻る':'対局に戻る';\n  drawAnalysisBoard(a);",
    1,
)

t = t.replace(
    "function closeAnalysis(){\n  $('analysisModal').classList.remove('show');\n  document.documentElement.classList.remove('analysisOpen');\n}\n",
    '''function closeAnalysis(){
  $('analysisModal').classList.remove('show');
  document.documentElement.classList.remove('analysisOpen');
  if(s.analysisReturnToReview){
    s.analysisReturnToReview=false;
    openReview();
  }
}
function renderReview(){
  let list=$('reviewList');list.innerHTML='';
  if(!s.reviews.length){
    list.innerHTML='<div class="analysisLine">評価された着手がありません。</div>';
    $('reviewAverage').textContent='-';$('reviewBestCount').textContent='0';$('reviewImproveCount').textContent='0';
    return;
  }
  let avg=Math.round(s.reviews.reduce((sum,a)=>sum+a.score,0)/s.reviews.length);
  $('reviewAverage').textContent=avg+'点';
  $('reviewBestCount').textContent=s.reviews.filter(a=>a.rank===1).length+'手';
  $('reviewImproveCount').textContent=s.reviews.filter(a=>a.score<75).length+'手';
  s.reviews.forEach((a,i)=>{
    let b=document.createElement('button');b.className='reviewItem';
    b.innerHTML=`<span class="reviewMoveNo">あなたの${i+1}手目</span><span class="reviewMeta"><b>${a.label}</b><span>候補${a.total}手中${a.rank}位${a.rank===1?'・最善手と一致':'・タップして比較'}</span></span><span class="reviewItemScore">${a.score}点</span>`;
    b.onclick=()=>{hideReview();s.analysis=a;s.analysisReturnToReview=true;openAnalysis();};
    list.appendChild(b);
  });
}
function openReview(){
  if(!s.reviews.length)return;
  renderReview();
  $('reviewModal').classList.add('show');
  document.documentElement.classList.add('analysisOpen');
  let d=$('reviewDialog');if(d)d.scrollTop=0;
}
function closeReview(){hideReview();}
''',
    1,
)

t = t.replace(
    "  $('replay').disabled=!s.history.length;render(true);",
    "  $('replay').disabled=!s.history.length;\n  if(s.mode==='cpu'&&s.reviews.length){\n    $('review').hidden=false;$('review').textContent=`対局レビュー（${s.reviews.length}手）`;\n    el.msg.textContent+=`　対局レビューで${s.reviews.length}手の評価を確認できます。`;\n  }\n  render(true);",
    1,
)

t = t.replace(
    "fromLink,saved:fromLink?null:{b:cloneBoard(s.b),history:s.history.slice(),logs:s.logs.slice()}",
    "fromLink,saved:fromLink?null:{b:cloneBoard(s.b),history:s.history.slice(),logs:s.logs.slice(),reviews:s.reviews.slice()}",
    1,
)

t = t.replace(
    "s.b=saved.b;s.history=saved.history;s.logs=saved.logs;el.log.textContent=s.logs.join('\\n');",
    "s.b=saved.b;s.history=saved.history;s.logs=saved.logs;s.reviews=saved.reviews||[];el.log.textContent=s.logs.join('\\n');\n    if(s.reviews.length){$('review').hidden=false;$('review').textContent=`対局レビュー（${s.reviews.length}手）`;}",
    1,
)

t = t.replace("$('replay').onclick=()=>startReplay(replayPayload());", "$('replay').onclick=()=>startReplay(replayPayload());\n$('review').onclick=openReview;", 1)
t = t.replace(
    "$('analysisModal').onclick=e=>{if(e.target===$('analysisModal'))closeAnalysis()};",
    "$('analysisModal').onclick=e=>{if(e.target===$('analysisModal'))closeAnalysis()};\n$('reviewClose').onclick=closeReview;\n$('reviewModal').onclick=e=>{if(e.target===$('reviewModal'))closeReview()};",
    1,
)
t = t.replace(
    "document.addEventListener('keydown',e=>{if(e.key==='Escape')closeAnalysis()});",
    "document.addEventListener('keydown',e=>{if(e.key==='Escape'){if($('analysisModal').classList.contains('show'))closeAnalysis();else if($('reviewModal').classList.contains('show'))closeReview();}});",
    1,
)

p.write_text(t, encoding='utf-8')
