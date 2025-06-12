import pytest
from utils.api.getUid import GetUID
from utils.api.getAccount import GetAccount

class TestCheckAccount:
    @pytest.mark.parametrize(
        "true_name, card_id",
        [
            # 保障隐私 身份证号模糊处理
            ["鲁尚武","4307032004xxxxxxxx"],
            ["范豪哲","4307032004xxxxxxxx"]
        ],ids=["MyInfo","ErrorInfo"]
    )
    def test_check_account(self, true_name, card_id):
        uid = GetUID().get_uid()
        account = GetAccount().get_account(true_name, card_id,uid)
        assert account is not None, "获取账户信息失败"

