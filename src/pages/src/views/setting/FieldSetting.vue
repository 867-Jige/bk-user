<template>
  <div v-bkloading="{ loading: isLoading, zIndex: 9 }" class="field-setting-content user-scroll-y">
    <bk-button class="add-field" theme="primary" @click="addField">
      <i class="user-icon icon-add-2 mr8" />
      {{ $t('添加字段') }}
    </bk-button>
    <div ref="rootRef">
      <bk-table
        class="field-setting-table"
        :data="tableData"
        :border="['outer']"
        :max-height="tableMaxHeight"
        show-overflow-tooltip>
        <template #empty>
          <Empty
            :is-data-empty="fieldData.isTableDataEmpty"
            :is-data-error="fieldData.isTableDataError"
            @handleUpdate="fetchFieldList"
          />
        </template>
        <bk-table-column prop="display_name" :label="$t('字段名称')">
          <template #default="{ row }">
            <div class="field-name">
              <span class="name">{{ row.display_name }}</span>
              <bk-tag theme="info" v-if="row.builtin">{{ $t('内置') }}</bk-tag>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column prop="name" :label="$t('英文标识')"></bk-table-column>
        <bk-table-column prop="data_type" :label="$t('字段类型')">
          <template #default="{ row }">
            <span>{{ switchType(row.data_type) }}</span>
          </template>
        </bk-table-column>
        <bk-table-column prop="required" :label="$t('是否必填')">
          <template #default="{ row }">
            <i :class="fieldStatus(row.required)"></i>
          </template>
        </bk-table-column>
        <bk-table-column prop="unique" :label="$t('是否唯一')">
          <template #default="{ row }">
            <i :class="fieldStatus(row.unique)"></i>
          </template>
        </bk-table-column>
        <bk-table-column prop="manager_editable" :label="$t('管理员可编辑')">
          <template #default="{ row }">
            <i :class="fieldStatus(row.manager_editable)"></i>
          </template>
        </bk-table-column>
        <bk-table-column prop="personal_center_visible" :label="$t('个人中心展示')">
          <template #default="{ row }">
            <i :class="fieldStatus(row.personal_center_visible)"></i>
          </template>
        </bk-table-column>
        <bk-table-column prop="personal_center_editable" :label="$t('个人中心可编辑')">
          <template #default="{ row }">
            <i :class="fieldStatus(row.personal_center_editable)"></i>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')">
          <template #default="{ row }">
            <span v-bk-tooltips="{ content: $t('该内置字段，不支持修改'), disabled: !row.builtin }">
              <bk-button text theme="primary" class="mr8" :disabled="row.builtin" @click="editField(row)">
                {{ $t('编辑') }}
              </bk-button>
            </span>
            <span v-bk-tooltips="{ content: $t('内置字段，不能删除'), disabled: !row.builtin }">
              <bk-button text theme="primary" :disabled="row.builtin" @click="deleteField(row)">
                {{ $t('删除') }}
              </bk-button>
            </span>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <!-- 添加字段的侧边栏 -->
    <bk-sideslider
      :width="640"
      :is-show="fieldData.isShow"
      :title="fieldData.title"
      :before-close="handleBeforeClose"
      quick-close>
      <FieldsAdd
        :set-type="fieldData.setType"
        :current-editor-data="fieldData.currentEditorData"
        @submitData="submitData"
        @handleCancel="handleCancel" />
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, Message } from 'bkui-vue';
import InfoBox from 'bkui-vue/lib/info-box';
import { inject, onMounted, reactive, ref } from 'vue';

import FieldsAdd from './FieldsAdd.vue';

import Empty from '@/components/Empty.vue';
import { useTableMaxHeight } from '@/hooks';
import { deleteCustomFields, getFields } from '@/http';
import { t } from '@/language/index';
import { useMainViewStore } from '@/store';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const tableMaxHeight = useTableMaxHeight(202);
const editLeaveBefore = inject('editLeaveBefore');
const fieldData = reactive({
  isShow: false,
  title: t('添加字段'),
  // 侧边栏区分添加字段、编辑字段
  setType: '',
  currentEditorData: {},
  isTableDataEmpty: false,
  isTableDataError: false,
});
const rootRef = ref();
const isLoading = ref(false);
const tableData = ref([]);

onMounted(() => {
  getFieldsList();
});

const getFieldsList = async () => {
  try {
    isLoading.value = true;
    fieldData.isTableDataEmpty = false;
    fieldData.isTableDataError = false;
    tableData.value = [];
    const res = await getFields();
    const { builtin_fields: builtinFields, custom_fields: customFields } = res.data || {};
    [builtinFields, customFields].forEach((fields, index) => {
      fields.forEach((item) => {
        item.builtin = index === 0;
        tableData.value.push(item);
      });
    });
    if (tableData.value.length === 0) {
      fieldData.isTableDataEmpty = true;
    }
  } catch (e) {
    console.warn(e);
    fieldData.isTableDataError = true;
  } finally {
    isLoading.value = false;
  }
};

// 字段类型转换
const switchType = (type: string) => {
  const typeObj = {
    multi_enum: t('枚举'),
    string: t('字符串'),
    bool: t('布尔值'),
    number: t('数值'),
    timer: t('日期'),
    enum: t('枚举'),
  };
  return typeObj[type];
};

// 展示字段状态
const fieldStatus = (type: boolean) => {
  if (type) {
    return 'user-icon icon-duihao-i';
  }
};

const addField = () => {
  fieldData.title = t('添加字段');
  fieldData.setType = 'add';
  fieldData.currentEditorData = {
    name: '', // 英文标识
    display_name: '', // 字段名称
    data_type: 'string', // 字段类型
    required: false, // 是否必填
    builtin: false, // 是否内置字段
    default: 0, // 默认值
    options: [
      { id: '', value: '' },
      { id: '', value: '' },
    ], // 枚举字段选项设置
    unique: false, // 是否唯一
    personal_center_visible: false, // 是否在个人中心可见
    personal_center_editable: false, // 是否在个人中心可编辑
    manager_editable: false, // 租户管理员是否可编辑
  };
  fieldData.isShow = true;
};

const editField = (item) => {
  fieldData.currentEditorData = item;
  fieldData.title = t('编辑字段');
  fieldData.setType = 'edit';
  fieldData.isShow = true;
};

const deleteField = (row) => {
  InfoBox({
    title: t('确认要删除吗？'),
    confirmText: t('确认删除'),
    onConfirm: () => {
      deleteCustomFields(row.id).then(() => {
        getFieldsList();
        Message({
          message: t('删除成功'),
          theme: 'success',
        });
      });
    },
  });
};
const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    fieldData.isShow = false;
  } else {
    fieldData.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};

const handleCancel = () => {
  fieldData.isShow = false;
  window.changeInput = false;
};

const submitData = (message) => {
  fieldData.isShow = false;
  window.changeInput = false;
  getFieldsList();
  Message({
    message,
    theme: 'success',
  });
};

const fetchFieldList = () => {
  getFieldsList();
};
</script>

<style lang="less" scoped>
.field-setting-content {
  height: calc(100vh - 104px);
  padding: 24px;

  .add-field {
    margin-bottom: 16px;
  }

  :deep(.field-setting-table) {
    .field-name {
      .name {
        margin: 0 8px;
        color: #63656e;
      }
    }

    .icon-duihao-i {
      font-size: 16px;
      color: #2dcb56;
    }

    .bk-table-footer {
      padding: 0 15px;
      background: #fff;
    }
  }
}

.blue-background-class {
  background: red;
}
</style>
