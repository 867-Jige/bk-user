<template>
  <bk-loading class="details-wrapper user-scroll-y" :loading="isLoading">
    <div ref="cardRef">
      <bk-form
        class="auth-source-form"
        ref="formRef"
        form-type="vertical"
        :model="authSourceData"
        :rules="rules">
        <div class="content-item">
          <p class="item-title">{{ $t('基本信息') }}</p>
          <bk-form-item :label="$t('名称')" property="name" required>
            <bk-input v-model="authSourceData.name" :placeholder="validate.name.message" @change="handleChange" />
          </bk-form-item>
          <bk-form-item :label="$t('是否启用')" required>
            <bk-switcher
              v-model="authSourceData.open"
              size="large"
              theme="primary"
            />
          </bk-form-item>
        </div>
        <div class="content-item">
          <p class="item-title">{{ $t('基础配置') }}</p>
          <div class="basic-config">
            <p v-if="onDataSources.length">{{ $t('以下数据源已开启「账密登录」') }}</p>
            <div class="on">
              <bk-overflow-title
                type="tips"
                class="source-name"
                v-for="(item, index) in onDataSources"
                :key="index">
                {{ item.data_source_name }}
              </bk-overflow-title>
            </div>
            <p v-if="notDataSources.length">{{ $t('以下数据源未开启「账密登录」') }}</p>
            <div class="off" v-for="(item, index) in notDataSources" :key="index">
              <bk-overflow-title
                type="tips"
                class="source-name">
                {{ item.data_source_name }}
                <bk-button text theme="primary" @click="handleOpen(item)">{{ $t('去开启') }}</bk-button>
              </bk-overflow-title>
            </div>
          </div>
        </div>
        <div class="content-item pb-[24px]">
          <p class="item-title">{{ $t('数据源匹配') }}</p>
          <div class="content-matching">
            <bk-exception
              v-if="onDataSources.length === 0"
              class="exception-part"
              type="empty"
              scene="part"
              :description="$t('暂无数据源匹配')"
            />
            <div class="content-box" v-else v-for="(item, index) in onDataSources" :key="index">
              <bk-overflow-title class="data-source-title">{{ item.data_source_name }}</bk-overflow-title>
              <div class="field-rules">
                <dl>
                  <dt>{{ $t('数据源字段') }}：</dt>
                  <bk-overflow-title
                    type="tips"
                    class="source-field"
                    v-for="(val, i) in item.field_compare_rules"
                    :key="i">
                    {{ val.source_field }}
                  </bk-overflow-title>
                </dl>
                <dl>
                  <dt>{{ $t('认证源字段') }}：</dt>
                  <bk-overflow-title
                    type="tips"
                    class="source-field"
                    v-for="(val, i) in item.field_compare_rules"
                    :key="i">
                    {{ val.target_field }}
                  </bk-overflow-title>
                </dl>
              </div>
              <span class="or" v-if="index !== 0">or</span>
            </div>
          </div>
        </div>
      </bk-form>
    </div>
    <div class="footer-wrapper">
      <div class="footer-div">
        <bk-button theme="primary" :loading="btnLoading" @click="handleSubmit">
          {{ $t('提交') }}
        </bk-button>
        <bk-button @click="handleCancel">
          {{ $t('取消') }}
        </bk-button>
      </div>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { onMounted, ref } from 'vue';

import { useValidate } from '@/hooks';
import { getDataSourceList, getIdpsDetails, patchIdps } from '@/http';
import router from '@/router/index';

const validate = useValidate();

const emit = defineEmits(['cancelEdit']);
const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
});

const formRef = ref();
const isLoading = ref(false);
const authSourceData = ref({
  name: '',
  open: false,
});
const onDataSources = ref([]);
const notDataSources = ref([]);
const btnLoading = ref(false);

const rules = {
  name: [validate.required, validate.name],
};

const cardRef = ref();

onMounted(async () => {
  try {
    isLoading.value = true;
    if (props.data.id) {
      const [authRes, dataRes] = await Promise.all([
        getIdpsDetails(props.data.id),
        getDataSourceList(''),
      ]);
      authSourceData.value = authRes.data;
      processMatchRules(dataRes.data);
    }
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
});

const processMatchRules = (list) => {
  const dataSourceIds = authSourceData.value.data_source_match_rules.map(item => item.data_source_id);
  onDataSources.value = list
    .filter(val => dataSourceIds.includes(val.id))
    .map(val => ({
      data_source_id: val.id,
      data_source_name: val.name,
      field_compare_rules: authSourceData.value.data_source_match_rules
        .find(item => item.data_source_id === val.id).field_compare_rules,
    }));
  notDataSources.value = list
    .filter(val => !dataSourceIds.includes(val.id) && val.plugin_id === 'local')
    .map(val => ({
      data_source_id: val.id,
      data_source_name: val.name,
    }));
};

const handleOpen = (item) => {
  router.push({
    name: 'newLocal',
    params: {
      type: 'local',
      id: item.data_source_id,
    },
  });
};

const handleChange = () => {
  window.changeInput = true;
};

const handleCancel = () => {
  emit('cancelEdit');
};

const handleSubmit = async () => {
  await formRef.value.validate();
  btnLoading.value = true;
  patchIdps({
    id: props.data.id,
    name: authSourceData.value.name,
  }).then(() => {
    Message({ theme: 'success', message: t('认证源更新成功') });
    window.changeInput = false;
    emit('cancelEdit');
  })
    .catch((e) => {
      console.warn(e);
      Message({ theme: 'error', message: t('认证源更新失败') });
    })
    .finally(() => {
      btnLoading.value = false;
    });
};
</script>

<style lang="less" scoped>
.details-wrapper {
  height: calc(100vh - 52px);
  padding: 20px 24px;
  background: #F5F7FA;

  .auth-source-form {
    .content-item {
      padding: 0 24px;
      margin-bottom: 16px;
      background: #fff;
      border-radius: 2px;
      box-shadow: 0 2px 4px 0 #1919290d;

      .item-title {
        padding: 16px 0;
        font-size: 14px;
        font-weight: 700;
      }

      .basic-config {
        padding-bottom: 12px;

        p {
          margin-bottom: 12px;
          font-size: 14px;
          color: #63656E;
        }

        .source-name {
          // width: 622px;
          height: 40px;
          padding-left: 24px;
          margin-bottom: 12px;
          line-height: 40px;
          color: #313238;
          background: #F5F7FA;
          border-radius: 2px;
        }

        .off {
          .source-name {
            position: relative;
            color: #C4C6CC;

            ::v-deep .text-ov {
              width: 535px;
            }

            .bk-button {
              position: absolute;
              top: 13px;
              right: 16px;
            }
          }
        }
      }

      .content-matching {
        padding-bottom: 8px;

        ::v-deep .exception-part {
          position: relative;
          width: 400px;

          .bk-exception-img {
            width: 340px;
            height: 170px;
          }

          .bk-exception-description {
            position: absolute;
            bottom: 0;
            font-size: 14px;
          }
        }

        .content-box {
          position: relative;

          .or {
            position: absolute;
            top: -16px;
            left: -22px;
            display: inline-block;
            width: 19px;
            height: 16px;
            line-height: 16px;
            color: #FE9C00;
            text-align: center;
            background: #FFF3E1;
            border-radius: 2px;

            &::before {
              position: absolute;
              top: -16px;
              left: 10px;
              width: 12px;
              height: 16px;
              border: 1px solid #DCDEE5;
              border-right: transparent;
              border-bottom: transparent;
              border-top-left-radius: 2px;
              content: '';
            }

            &::after {
              position: absolute;
              top: 16px;
              left: 10px;
              width: 12px;
              height: 16px;
              border: 1px solid #DCDEE5;
              border-top: transparent;
              border-right: transparent;
              border-bottom-left-radius: 2px;
              content: '';
            }
          }
        }

        .data-source-title {
          position: relative;
          padding: 0 24px;
          line-height: 32px;
          background: #F0F1F5;
          border-radius: 2px 2px 0 0;
        }

        .field-rules {
          display: flex;
          margin-bottom: 16px;
          background: #FAFBFD;
          border-radius: 2px;

          dl {
            padding: 12px 0 12px 50px;;

            dt {
              font-size: 14px;
              line-height: 22px;
              color: #979BA5;
            }

            .source-field {
              max-width: 250px;
              min-width: 120px;
              font-size: 14px;
              line-height: 22px;
              color: #313238;
            }
          }
        }
      }

      ::v-deep .bk-form-item {
        padding-bottom: 24px;
        margin-bottom: 0;
        font-size: 14px;

        &:last-child {
          margin-bottom: 16px;
        }

        .bk-radio-button {
          .bk-radio-button-label {
            font-size: 14px !important;
          }
        }

        .bk-radio-label {
          font-size: 14px !important;
        }

        .error-text {
          font-size: 12px;
          line-height: 1;
          color: #ea3636;
          animation: form-error-appear-animation .15s;
        }
      }

      .data-source-matching {
        width: 622px;
        margin-left: 59px;
        border-radius: 2px;

        .hover-item {
          cursor: pointer;
        }

        .matching-item {
          position: relative;
          padding: 16px 16px 16px 24px;
          margin-bottom: 16px;
          background: #F5F7FA;

          .bk-sq-icon {
            position: absolute;
            top: -6px;
            right: -6px;
            font-size: 20px;
            color: #EA3636;
          }

          .or {
            position: absolute;
            top: -16px;
            left: -22px;
            display: inline-block;
            width: 19px;
            height: 16px;
            line-height: 16px;
            color: #FE9C00;
            text-align: center;
            background: #FFF3E1;
            border-radius: 2px;

            &::before {
              position: absolute;
              top: -27px;
              left: 10px;
              width: 12px;
              height: 27px;
              border: 1px solid #DCDEE5;
              border-right: transparent;
              border-bottom: transparent;
              border-top-left-radius: 2px;
              content: '';
            }

            &::after {
              position: absolute;
              top: 16px;
              left: 10px;
              width: 12px;
              height: 27px;
              border: 1px solid #DCDEE5;
              border-top: transparent;
              border-right: transparent;
              border-bottom-left-radius: 2px;
              content: '';
            }
          }

          ::v-deep .bk-form-item {
            padding-bottom: 24px;
            margin-bottom: 0;
            margin-left: 0;
            font-size: 14px;

            &:last-child {
              margin-bottom: 0;
            }
          }

          .item-flex-header {
            display: flex;
            align-items: center;

            ::v-deep .bk-form-item {
              padding-bottom: 0;
              margin-bottom: 0;
              margin-left: 0;
              font-size: 14px;

              &:last-child {
                margin-left: 16px;
              }
            }
          }

          .item-flex {
            position: relative;
            display: flex;
            padding-bottom: 8px;
            align-items: center;

            ::v-deep .bk-form-item {
              padding-bottom: 0;
              margin-bottom: 0;
              margin-left: 0;
              font-size: 14px;
            }

            .auth-source-fields {
              margin-left: 16px;
            }

            .user-icon {
              font-size: 16px;
              color: #dcdee5;

              &:hover {
                color: #c4c6cc;
              }
            }

            .icon-plus-fill {
              position: absolute;
              top: 9px;
              right: 35px;
            }

            .icon-minus-fill {
              position: absolute;
              top: 9px;
              right: 5px;
            }

            .and {
              position: absolute;
              top: -12px;
              left: -24px;
              display: inline-block;
              width: 24px;
              height: 16px;
              line-height: 16px;
              color: #14A568;
              text-align: center;
              background: #E4FAF0;
              border-radius: 2px;

              &::before {
                position: absolute;
                top: -12px;
                left: 12px;
                width: 12px;
                height: 12px;
                border: 1px solid #DCDEE5;
                border-right: transparent;
                border-bottom: transparent;
                border-top-left-radius: 2px;
                content: '';
              }

              &::after {
                position: absolute;
                top: 16px;
                left: 12px;
                width: 12px;
                height: 12px;
                border: 1px solid #DCDEE5;
                border-top: transparent;
                border-right: transparent;
                border-bottom-left-radius: 2px;
                content: '';
              }
            }
          }
        }
      }

      .add-data-source {
        display: flex;
        width: 622px;
        height: 32px;
        margin-left: 59px;
        font-size: 14px;
        color: #3A84FF;
        cursor: pointer;
        background: #F0F5FF;
        border: 1px dashed #A3C5FD;
        border-radius: 2px;
        align-items: center;
        justify-content: center;

        span {
          margin-left: 5px;
        }
      }
    }
  }

  .footer-wrapper {
    .bk-button {
      width: 88px;
      margin-right: 8px;
    }
  }
}
</style>
