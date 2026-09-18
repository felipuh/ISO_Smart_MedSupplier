import React from 'react';
import { S3InlineAlert } from '@smart3ai/design-system';
import { useI18n } from '../../context/I18nContext';

const CrudErrorBanner = ({ message, onClose }) => {
  const { t } = useI18n();

  if (!message) return null;

  return (
    <S3InlineAlert
      message={message}
      onClose={onClose}
      dismissLabel={t('common.buttons.dismissError')}
      variant="danger"
    />
  );
};

export default CrudErrorBanner;
