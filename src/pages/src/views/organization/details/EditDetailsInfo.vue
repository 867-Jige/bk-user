<template>
  <div ref="boxRef" class="operation-wrapper pt-[8px]">
    <div ref="cardRef" class="operation-content">
      <div class="operation-card">
        <div class="operation-content-title">{{ $t('基本信息') }}</div>
        <div class="operation-content-info">
          <bk-form
            class="operation-content-form"
            ref="basicRef"
            form-type="vertical"
            :model="formData"
            :rules="rulesBasicInfo"
          >
            <bk-form-item :label="$t('租户名称')" property="name" required>
              <bk-input v-model="formData.name" :placeholder="validate.name.message" @focus="handleChange" />
            </bk-form-item>
            <bk-form-item :label="$t('租户ID')" property="id" required>
              <bk-input
                v-model="formData.id"
                disabled
              />
            </bk-form-item>
            <bk-form-item :label="$t('人员数量')">
              <bk-radio-group
                :model-value="formData.feature_flags?.user_number_visible"
                @change="changeVisible"
              >
                <bk-radio-button :label="true">{{ $t('显示') }}</bk-radio-button>
                <bk-radio-button :label="false">{{ $t('隐藏') }}</bk-radio-button>
              </bk-radio-group>
            </bk-form-item>
          </bk-form>
          <bk-upload
            theme="picture"
            with-credentials
            :multiple="false"
            :files="files"
            :handle-res-code="handleRes"
            :url="formData.logo"
            :custom-request="customRequest"
            :size="2"
            @delete="handleDelete"
            @error="handleError"
          />
        </div>
      </div>
      <div class="operation-card">
        <div class="operation-content-title">{{ $t('管理员') }}</div>
        <bk-form ref="userRef" :model="formData">
          <bk-table
            class="operation-content-table"
            :border="['col', 'outer']"
            :data="formData.managers"
            :columns="columns"
          >
          </bk-table>
        </bk-form>
      </div>
    </div>
    <div class="footer" :class="{ 'fixed': isScroll}">
      <bk-button theme="primary" @click="handleSubmit" :loading="state.isLoading">
        {{ $t('提交') }}
      </bk-button>
      <bk-button @click="() => $emit('handleCancel')">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="tsx">
import { Message } from 'bkui-vue';
import { ref, reactive, computed, nextTick, defineProps, defineEmits, watch, defineExpose } from 'vue';
import { getBase64 } from '@/utils';
import MemberSelector from '@/views/tenant/MemberSelector.vue';
import { getTenantOrganizationUsersList, putTenantOrganizationDetails } from '@/http';
import PhoneInput from '@/components/phoneInput.vue';
import { useValidate, useButtonFixed } from '@/hooks';
import { t } from '@/language/index';

interface TableItem {
  username: string;
  full_name: string;
  email: string;
  phone: string;
  phone_country_code: string;
}
interface TableColumnData {
  index: number;
  data: TableItem;
}

const props = defineProps({
  tenantsData: {
    type: Object,
    default: {},
  },
  managers: {
    type: Array,
    default: [],
  },
});

const validate = useValidate();
const emit = defineEmits(['updateTenantsList', 'handleCancel']);

const basicRef = ref();
const userRef = ref();
const formData = reactive(JSON.parse(JSON.stringify({ ...props.tenantsData })));
const state = reactive({
  username: "",
  count: 0,
  list: [],
  isLoading: false,
});

const params = reactive({
  id: props.tenantsData.id,
  keyword: "",
  page: 1,
  pageSize: 10,
});

const rulesBasicInfo = {
  name: [validate.required, validate.name],
  id: [validate.required],
};

const rulesUserName = {
  username: [validate.required],
};

const files = computed(() => {
  const img = [];
  if (formData.logo !== "") {
    img.push({
      url: formData.logo,
    });
    return img;
  }
  return [];
});

const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};
const customRequest = (event) => {
  getBase64(event.file)
    .then((res) => {
      formData.logo = res;
    })
    .catch((e) => {
      console.warn(e);
    });
  handleChange();
};

const handleDelete = () => {
  formData.logo = "";
  handleChange();
};

const handleError = (file) => {
  if (file.size > (2 * 1024 * 1024)) {
    Message({ theme: 'error', message: t('图片大小超出限制，请重新上传') });
  }
};

const fieldItemFn = (row: any) => {
  const { column, index, data } = row;
  return (
    <bk-form-item
      error-display-type="tooltips"
      property={`managers.${index}.${column.field}`}
      rules={rulesUserName[column.field]}
    >
      {!data.id ? (
        column.field === "username" ? (
          <MemberSelector
            v-model={formData.managers[index][column.field]}
            state={state}
            params={params}
            onSelectList={selectList}
            onScrollChange={scrollChange}
            onSearchUserList={fetchUserList}
          />
        ) : (
          column.field === 'phone'
            ? <PhoneInput
                id="phone-id"
                form-data={formData.managers[index]}
                disabled />
            : <bk-input
                v-model={formData.managers[index][column.field]}
                disabled={column.field !== "username"}
              />
        )
      ) : (
        column.field === 'phone'
          ? <PhoneInput
              id="phone-id"
              form-data={formData.managers[index]}
              telError={formData.managers[index].error}
              disabled={data.id}
              tooltips={true}
              onChangeCountryCode={(code: string) => changeCountryCode(code, index)}
              onChangeTelError={(value: boolean) => changeTelError(value, index)} />
          : <bk-input
              v-model={formData.managers[index][column.field]}
              disabled={data.id}
            />
      )}
    </bk-form-item>
  );
};

const changeCountryCode = (code: string, index: number) => {
  formData.managers[index].phone_country_code = code;
};

const changeTelError = (value: boolean, index: number) => {
  formData.managers[index].error = value;
};

const columns = [
  {
    label: t('用户名'),
    field: "username",
    render: fieldItemFn,
  },
  {
    label: t('全名'),
    field: "full_name",
    render: fieldItemFn,
  },
  {
    label: t('邮箱'),
    field: "email",
    render: fieldItemFn,
  },
  {
    label: t('手机号'),
    field: "phone",
    render: fieldItemFn,
  },
  {
    label: t('操作'),
    field: "",
    width: 65,
    render: ({ data, index }: TableColumnData) => {
      return (
        <div style="font-size: 16px;">
          <bk-button
            style="margin: 0 10px;"
            text
            onClick={handleItemChange.bind(this, index, 'add')}
          >
            <i class="user-icon icon-plus-fill" />
          </bk-button>
          <bk-button
            text
            disabled={formData.managers.length === 1}
            onClick={handleItemChange.bind(this, index, 'remove')}
          >
            <i class={['user-icon icon-minus-fill', { 'forbid': formData.managers.length === 1 }]} />
          </bk-button>
        </div>
      );
    },
  },
];

watch(() => props.managers, (value) => {
  if (value.length === 0) {
    formData.managers.splice(1, 0, getTableItem());
  }
}, {
  deep: true,
  immediate: true,
});

/**
 * 获取表格数据
 */
function getTableItem(): TableItem {
  return {
    username: "",
    full_name: "",
    email: "",
    phone: "",
    phone_country_code: "86",
  };
}

function handleItemChange(index: number, action: 'add' | 'remove') {
  if(action === 'add') {
    formData.managers.splice(index + 1, 0, getTableItem());
  } else if (action === 'remove') {
    formData.managers.splice(index, 1);
  }

  window.changeInput = true;
  fetchUserList('');
}

const boxRef = ref();
const cardRef = ref();
// footer按钮状态
const isScroll = useButtonFixed(boxRef, cardRef, 54);

// 获取管理员列表
const fetchUserList = (value: string) => {
  params.keyword = value;
  params.page = 1;
  if (params.id) {
    getTenantOrganizationUsersList(params).then((res) => {
      const list = formData.managers.map((item) => item.id);
      state.count = res.data.count;
      state.list = res.data.results.map(item => ({
        ...item,
        disabled: list.includes(item.id),
      }));
    });
  }
}
fetchUserList('');

const selectList = (list) => {
  formData.managers = formData.managers.filter(item => item.id);
  if (list?.length) {
    formData.managers.push(...list);
    userRef.value.validate();
  } else {
    nextTick(() => {
      const managers = [{
        username: "",
        full_name: "",
        email: "",
        phone: "",
        phone_country_code: "86",
      }];

      formData.managers.push(...managers);
    });
  }
};

const scrollChange = () => {
  params.page += 1;
  getTenantOrganizationUsersList(params).then((res) => {
    const list = formData.managers.map((item) => item.id);
    state.count = res.data.count;
    state.list.push(...res.data.results.map(item => ({
      ...item,
      disabled: list.includes(item.id),
    })));
  });
}

// 校验表单
async function handleSubmit() {
  const validationPromises = [
    basicRef.value.validate(),
    userRef.value.validate(),
  ];

  await Promise.all(validationPromises);
  state.isLoading = true;
  putTenantOrganization();
}

function putTenantOrganization() {
  const manager_ids = formData.managers.map(item => item.id);
  const params = {
    name: formData.name,
    logo: formData.logo,
    feature_flags: {
      user_number_visible: formData.feature_flags?.user_number_visible,
    },
    manager_ids,
  };

  if (!params.logo) delete params.logo;

  putTenantOrganizationDetails(formData.id, params)
    .then(() => {
      emit('updateTenantsList');
    })
    .catch((e) => {
      console.warn(e);
    })
    .finally(() => {
      state.isLoading = false;
    });
}

const handleChange = () => {
  window.changeInput = true;
}

const changeVisible = (status: boolean) => {
  formData.feature_flags.user_number_visible = status;
}

defineExpose({
  boxRef,
  cardRef,
});
</script>

<style lang="less" scoped>
@import url("@/css/tenantEditStyle.less");

::v-deep .bk-select {
  .angle-up {
    display: none !important;
  }
}
</style>
