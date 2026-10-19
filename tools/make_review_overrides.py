# Build tools/review_overrides.json from the legal team's returned review (export/review-returned.xlsx)
# Reviewer edits are kept when verified against the official texts (src/*_art.json, src/nd356.txt);
# wrong/non-existent article citations are replaced by the verified location (see FIX notes).
import json, openpyxl
R='/workspace/cyberquiz'
A='Luật An ninh mạng số 116/2025/QH15'; B='Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15'; N='Nghị định 356/2025/NĐ-CP'
CN='Cẩm nang “Kết nối không tổn thương” 2026 (Chiến dịch Không Một Mình)'
N328='Nghị định 328/2026/NĐ-CP ngày 19/8/2026 quy định phòng, chống tin giả, tin sai sự thật'
FIX={ # id: (legal, how, ambiguous?)
 20:(f'Khoản 3 Điều 51 Luật Trẻ em số 102/2016/QH13; Điều 22, Điều 23 Nghị định 56/2017/NĐ-CP; {CN}','Điều 29 Luật Trẻ em không quy định tổng đài; tổng đài điện thoại quốc gia bảo vệ trẻ em quy định tại khoản 3 Điều 51 Luật Trẻ em, số ngắn 03 số tại Điều 22–23 NĐ 56/2017 (đối chiếu văn bản trên thuvienphapluat.vn).',True),
 112:(N328,'Giữ ý kiến bổ sung ngày ban hành; sửa trích yếu theo đúng trích yếu chính thức trên vanban.chinhphu.vn ("Quy định phòng, chống tin giả, tin sai sự thật").',True),
 166:(f'Điểm d khoản 1 Điều 7 {A}; {N328}','Thu hẹp "Khoản 1 Điều 7, Điều 16" về đúng điểm d khoản 1 Điều 7 (thông tin sai sự thật gây hoang mang trong Nhân dân); Điều 16 không trực tiếp quy định tin giả nên bỏ; chuẩn tên NĐ 328.',True),
 169:(f'Điều 32 Bộ luật Dân sự 2015; Điều 9 {B}','Giữ Điều 32 BLDS (quyền đối với hình ảnh); khoản 1 Điều 3 Luật BVDLCN là nguyên tắc tuân thủ Hiến pháp, không liên quan – thay bằng Điều 9 (sự đồng ý của chủ thể dữ liệu).',True),
 192:(f'Điều 32 Bộ luật Dân sự 2015; Điều 9 {B}','Như câu 169: thay khoản 1 Điều 3 bằng Điều 9 Luật BVDLCN (sự đồng ý).',True),
 172:(f'Điều 3, Điều 9 {B}','Giữ Điều 9 (sự đồng ý) theo ý kiến; bổ sung Điều 3 (nguyên tắc chỉ xử lý đúng phạm vi, mục đích).',False),
 177:(f'Khoản 3 Điều 7 {A}','Điểm b khoản 2 Điều 7 là hành vi kích động bạo lực, không phải chiếm tài khoản – sửa thành khoản 3 Điều 7 (xâm nhập, chiếm quyền điều khiển trái phép).',False),
 197:(f'Khoản 5 Điều 16 {A}; Điều 24 {B}','"Điều 3" Luật BVDLCN quá chung – thay bằng Điều 24 (bảo vệ dữ liệu cá nhân của trẻ em); chuẩn Điều 16 ANM về khoản 5 như các câu trẻ em khác.',False),
 235:(f'Điểm b khoản 1 Điều 40 {A}','Khoản 2 Điều 25 và Điều 39 không quy định việc kết nối giám sát; nghĩa vụ kết nối hệ thống giám sát về Trung tâm An ninh mạng quốc gia nằm tại điểm b khoản 1 Điều 40.',False),
 458:(f'Khoản 2 Điều 39 {N}','Luật BVDLCN chỉ có 39 điều – không có Điều 45; chức năng Cổng TTQG tại khoản 2 Điều 39 NĐ 356 (giữ phần NĐ của ý kiến).',False),
 521:(f'Khoản 2 Điều 39 {N}','Không tồn tại Điều 45 Luật BVDLCN; dùng khoản 2 Điều 39 NĐ 356.',False),
 577:(f'Khoản 5 Điều 34 {N}','Không tồn tại Điều 45 Luật BVDLCN; Bộ Công an xây dựng, quản lý, vận hành Cổng TTQG tại khoản 5 Điều 34 NĐ 356.',False),
 467:(f'Khoản 2 Điều 6 {N}; Điều 9 {B}','Điều 9 Luật BVDLCN không có khoản 6; trách nhiệm chứng minh sự đồng ý tại khoản 2 Điều 6 NĐ 356.',False),
 469:(f'Khoản 1 Điều 9 {N}; Điều 30 {B}','Điều 2 Luật BVDLCN không có khoản 15, Điều 24 là dữ liệu trẻ em; định nghĩa xử lý dữ liệu lớn tại khoản 1 Điều 9 NĐ 356, Điều 30 Luật.',False),
 596:(f'Khoản 1 Điều 9 {N}; Điều 30 {B}','Như câu 469.',False),
 470:(f'Khoản 1 Điều 8 {N}; Điều 27 {B}','Điều 25 Luật là lao động, Điều 21 NĐ là danh mục dịch vụ; tài chính – ngân hàng đánh giá tuân thủ 01 năm/lần tại khoản 1 Điều 8 NĐ 356 (Điều 27 Luật).',False),
 471:(f'Khoản 1, khoản 2 Điều 7 {N}; Điều 17 {B}','Điều 23 Luật là thông báo vi phạm, Điều 19 NĐ là ĐGTĐ; chuyển giao dữ liệu (thỏa thuận; bảo mật vật lý, mã hóa, ẩn danh) tại khoản 1–2 Điều 7 NĐ 356, Điều 17 Luật.',False),
 473:(f'Khoản 4 Điều 5 {N}; Điều 14 {B}','Điều 15 Luật là cung cấp dữ liệu, Điều 12 NĐ là điện toán đám mây; thời hạn xóa 20 ngày tại khoản 4 Điều 5 NĐ 356; xóa dữ liệu tại Điều 14 Luật.',False),
 543:(f'Khoản 4 Điều 5 {N}; Điều 14 {B}','Như câu 473.',False),
 474:(f'Khoản 2 Điều 5 {N}; Điều 4 {B}','Điều 14 Luật/Điều 13 NĐ không quy định thời hạn này; 15 ngày ngừng xử lý tại khoản 2 Điều 5 NĐ 356.',False),
 475:(f'Khoản 2 Điều 5 {N}; Điều 10 {B}','Thời hạn phản hồi 02 ngày làm việc nằm tại khoản 2 Điều 5 NĐ 356 (Điều 10 Luật quy định quyền rút lại sự đồng ý).',False),
 476:(f'Khoản 3 Điều 2 {B}; điểm k khoản 1 Điều 4 {N}','Điều 4 Luật là quyền và nghĩa vụ chủ thể; danh mục dữ liệu nhạy cảm (tài khoản, lịch sử giao dịch ngân hàng) tại điểm k khoản 1 Điều 4 NĐ 356.',False),
 494:(f'Khoản 2 Điều 2 {B}; khoản 7 Điều 3 {N}','Điều 4 Luật không phải danh mục dữ liệu; số định danh, số hộ chiếu là dữ liệu cơ bản tại khoản 7 Điều 3 NĐ 356.',False),
 509:(f'Khoản 3 Điều 2 {B}; điểm d, điểm đ khoản 1 Điều 4 {N}','Dữ liệu sức khỏe, sinh trắc học thuộc danh mục nhạy cảm tại điểm d, đ khoản 1 Điều 4 NĐ 356.',False),
 510:(f'Khoản 3 Điều 2 {B}; điểm b khoản 1 Điều 4 {N}','Quan điểm chính trị, tôn giáo tại điểm b khoản 1 Điều 4 NĐ 356.',False),
 496:(f'Khoản 5 Điều 18, khoản 5 Điều 19 {N}','Điều 20 Luật/Điều 22 NĐ không quy định; trả kết quả 15 ngày tại khoản 5 Điều 18, 19 NĐ 356.',False),
 505:(f'Khoản 6 Điều 18, khoản 6 Điều 19 {N}','Thời hạn hoàn thiện 30 ngày tại khoản 6 Điều 18, 19 NĐ 356.',False),
 506:(f'Điểm a khoản 2 Điều 19 và Mẫu số 10 Phụ lục {N}','Mẫu số 10 quy định tại điểm a khoản 2 Điều 19 (Điều 20 là cập nhật hồ sơ).',False),
 501:(f'Khoản 2 Điều 16 {N}','Điều 28 NĐ là thông báo vi phạm; hồ sơ năng lực tại khoản 2 Điều 16.',False),
 502:(f'Điểm b khoản 1 Điều 16 {N}','Tối thiểu 03 nhân sự tại điểm b khoản 1 Điều 16.',False),
 585:(f'Điểm b khoản 1 Điều 16 {N}','Như câu 502.',False),
 503:(f'Điểm b khoản 2 Điều 15 {N}','Điều 29 NĐ là vi phạm dữ liệu vị trí/sinh trắc; 03 năm kinh nghiệm tại điểm b khoản 2 Điều 15.',False),
 507:(f'Điểm a khoản 2 Điều 13 {N}','Điều 27 NĐ là thu hồi Giấy chứng nhận; trình độ cao đẳng tại điểm a khoản 2 Điều 13.',False),
 556:(f'Điểm a khoản 2 Điều 13 {N}','Như câu 507.',False),
 508:(f'Khoản 1 Điều 13 {N}','Chỉ định bằng văn bản chính thức tại khoản 1 Điều 13.',False),
 511:(f'Khoản 1 Điều 14 {N}','Nhiệm vụ bộ phận bảo vệ dữ liệu tại khoản 1 Điều 14.',False),
 512:(f'Điểm b khoản 2 Điều 13 {N}','Các lĩnh vực kinh nghiệm tại điểm b khoản 2 Điều 13.',False),
 513:(f'Điểm b khoản 2 Điều 13 {N}','02 năm kinh nghiệm tại điểm b khoản 2 Điều 13.',False),
 555:(f'Điểm b khoản 2 Điều 13 {N}','Như câu 513.',False),
 516:(f'Khoản 3 Điều 38 {B}; khoản 2 Điều 41 {N}','Khoản 2 Điều 20 NĐ là cập nhật hồ sơ; ngưỡng 100 nghìn chủ thể (tích lũy) với doanh nghiệp siêu nhỏ tại khoản 2 Điều 41 NĐ 356, khoản 3 Điều 38 Luật.',False),
 517:(f'Khoản 2 Điều 40 {N}','Luật BVDLCN không có Điều 44; kinh phí của cơ quan nhà nước do NSNN bảo đảm tại khoản 2 Điều 40 NĐ 356.',False),
 591:(f'Khoản 2 Điều 40 {N}','Như câu 517.',False),
 518:(f'Điểm b khoản 1 Điều 26 {N}','Điều 32 NĐ không quy định; cấp lại 05 ngày làm việc tại điểm b khoản 1 Điều 26.',False),
 519:(f'Khoản 3 Điều 27 {N}','Điều 34 NĐ là nhiệm vụ cơ quan chuyên trách; nộp lại trong 05 ngày làm việc tại khoản 3 Điều 27.',False),
 597:(f'Khoản 3 Điều 27 {N}','Như câu 519.',False),
 520:(f'Điểm b khoản 1 Điều 27 {N}','Thu hồi khi không kinh doanh 12 tháng tại điểm b khoản 1 Điều 27 (Điều 33 NĐ không quy định).',False),
 590:(f'Điểm b khoản 1 Điều 27 {N}','Như câu 520.',False),
 527:(f'Khoản 4 Điều 25 {N}','Thẩm định, quyết định cấp trong 30 ngày tại khoản 4 Điều 25 (Điều 31 NĐ là kiểm tra).',False),
 528:(f'Điểm a khoản 1 Điều 25 và Mẫu số 04 Phụ lục {N}','Bổ sung điều khoản dẫn chiếu Mẫu số 04.',False),
 571:(f'Điểm a khoản 1 Điều 25 và Mẫu số 04 Phụ lục {N}','Như câu 528.',False),
 529:(f'Khoản 1 Điều 24 {N}','Thẩm quyền cấp của Bộ Công an tại khoản 1 Điều 24 (Điều 31 NĐ là kiểm tra).',False),
 595:(f'Khoản 1 Điều 24 {N}','Như câu 529.',False),
 530:(f'Khoản 3 Điều 23 {N}','Đánh giá tín nhiệm 01 năm/lần tại khoản 3 Điều 23 (Điều 30 NĐ không quy định).',False),
 531:(f'Điểm a khoản 2 Điều 22 {N}','Người đứng đầu phụ trách chuyên môn là công dân VN thường trú tại VN – điểm a khoản 2 Điều 22.',False),
 532:(f'Điều 21 {N}','Danh mục dịch vụ xử lý dữ liệu cá nhân tại Điều 21 (Điều 26 NĐ là cấp lại).',False),
 535:(f'Khoản 4 Điều 25 {N}','Cấp bản giấy và bản điện tử tại khoản 4 Điều 25.',False),
 548:(f'Khoản 1 Điều 42 {N} ngày 31/12/2025 quy định chi tiết Luật Bảo vệ dữ liệu cá nhân','Giữ ý kiến; bổ sung điều khoản hiệu lực (khoản 1 Điều 42).',False),
 551:(f'Điểm a khoản 1 Điều 29 {N}; Điều 23, Điều 31 {B}','Điều 22 Luật là cập nhật hồ sơ, Điều 18 NĐ là chuyển xuyên biên giới; 72 giờ tại điểm a khoản 1 Điều 29 NĐ 356.',False),
 552:(f'Điểm c khoản 1 Điều 29 {N}','Điều 19 NĐ là ĐGTĐ; lưu hồ sơ tối thiểu 5 năm tại điểm c khoản 1 Điều 29.',False),
 579:(f'Điểm c khoản 1 Điều 29 {N}','Như câu 552.',False),
 553:(f'Khoản 4 Điều 31 {N}','NĐ 356 có 42 điều, Điều 36 là nhiệm vụ của bộ; báo trước 15 ngày tại khoản 4 Điều 31.',False),
 554:(f'Khoản 4 Điều 31 {N}','Kiểm tra đột xuất không cần thông báo trước tại khoản 4 Điều 31 (không phải khoản 3 Điều 36).',False),
 572:(f'Khoản 8 Điều 23 {N}','Xác thực danh tính theo pháp luật định danh và xác thực điện tử tại khoản 8 Điều 23.',False),
 578:(f'Điểm b khoản 5 Điều 10 {N}; Điều 30 {B}','Điều 21 Luật là ĐGTĐ; cơ chế giám sát AI hai phương diện tại điểm b khoản 5 Điều 10 NĐ 356.',False),
 584:(f'Khoản 2 Điều 28 và Mẫu số 08 Phụ lục {N}','Bổ sung điều khoản dẫn chiếu Mẫu số 08.',False),
 586:(f'Điểm b khoản 3 Điều 12 {N}','Nhà thầu phụ điện toán đám mây tại điểm b khoản 3 Điều 12 (Điều 23 NĐ là nghĩa vụ tổ chức kinh doanh dịch vụ).',False),
 600:(f'Khoản 4 Điều 18 và Mẫu số 01b Phụ lục {N}','Mẫu số 01b (thông báo gửi hồ sơ chuyển xuyên biên giới đối với cá nhân) dẫn chiếu tại khoản 4 Điều 18.',False),
 546:(f'Khoản 2 Điều 5 {N}; Điều 10 {B}','Điều 11 Luật là thu thập dữ liệu. Mức gia hạn khác nhau theo loại yêu cầu (ngừng xử lý: 15 ngày; chỉnh sửa: 10 ngày; xóa: 20 ngày – Điều 5 NĐ 356), nên sửa câu hỏi cho rõ "yêu cầu ngừng xử lý" để đáp án 15 ngày đúng luật.',True),
}
SIT={150:'Luật An ninh mạng số 116/2025/QH15 được Quốc hội thông qua ngày nào?',
     546:'Yêu cầu ngừng xử lý dữ liệu của chủ thể dữ liệu quá phức tạp. Bên kiểm soát được gia hạn tối đa bao lâu?'}
old={x['id']:x for x in json.load(open(R+'/questions.json',encoding='utf-8'))['questions']}
ws=openpyxl.load_workbook(R+'/export/review-returned.xlsx')['Tất cả']
ov={};rep=[]
for r in ws.iter_rows(min_row=2,values_only=True):
    i,lv,sit,leg,note,kl=r[0],r[1],r[4],r[12],r[17] or '',r[18] or ''
    o=old[i]
    if leg==o['legal'] and sit==o['situation'] and kl!='Sửa': continue
    e={};how='Áp dụng đúng nội dung tổ pháp chế đã sửa (đã đối chiếu văn bản gốc).';amb=False
    if leg!=o['legal']: e['legal']=leg
    if i in FIX: e['legal'],how,amb=FIX[i]
    if i in SIT: e['situation']=SIT[i]
    if i==150: how='Áp dụng sửa của pháp chế: "ban hành" → "thông qua" (bỏ ghi chú [Gốc]); viết đầy đủ tên luật; ngày thông qua 10/12/2025 đã đối chiếu văn bản luật.'
    if not e: how='Pháp chế đánh dấu Sửa nhưng không thay đổi nội dung – giữ nguyên.'
    ov[i]=e
    rep.append(dict(id=i,level=lv,old_sit=o['situation'],new_sit=e.get('situation',o['situation']),old_legal=o['legal'],new_legal=e.get('legal',o['legal']),note=note,kl=kl,how=how,amb=amb))
json.dump(ov,open(R+'/tools/review_overrides.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump(rep,open('/tmp/review_report.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(rep),'flagged;',sum(1 for x in rep if x['new_legal']!=x['old_legal'] or x['new_sit']!=x['old_sit']),'changed;',sum(x['amb'] for x in rep),'ambiguous;',len([i for i in FIX if i not in ov]),'FIX unused',[i for i in FIX if i not in ov])
