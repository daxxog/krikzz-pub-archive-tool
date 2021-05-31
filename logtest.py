from logging import getLogger, basicConfig, DEBUG
basicConfig(level=DEBUG)
log = getLogger(__name__)

log.debug('debug')
log.info('info')
log.warning('warn')
